#!/usr/bin/env bash
# =============================================================================
# runpod_train.sh — Saatlik kiralık NVIDIA pod'unda (RunPod / Lambda / Vast.ai) Gaussian
# splat eğitimi: bağımlılık kurulumu → (COLMAP poz kestirimi | hazır poz) → nerfstudio
# splatfacto (gsplat) eğitimi → .ply dışa aktarma → sonuçları TEK arşive koyma.
#
# POD İÇİNDE çalışır. Önerilen imaj: CUDA "devel" içeren bir PyTorch imajı (gsplat ilk
# çalıştırmada CUDA çekirdeklerini derler; nvcc gerekir). Ör. RunPod PyTorch şablonları.
# İmaj/sürüm uyumu bu ortamda TEST EDİLMEDİ (GPU yok) — ilk gerçek koşuda doğrulanacak.
#
# Kullanım (pod'da):
#   bash runpod_train.sh                         # aşağıdaki varsayılanlarla
#   DATA_ARCHIVE=/workspace/in/TYAT.tar METHOD=splatfacto-big MAX_ITERS=30000 bash runpod_train.sh
#   DRY_RUN=1 bash runpod_train.sh               # yalnız komutları yazdır
#
# Girdi arşivi (Mac'te pipeline.py çıktısından hazırlanır, bkz. cloud/README.md):
#   <arşiv>/images/            perspektif görüntüler (zorunlu)
#   <arşiv>/sparse/0/          COLMAP modeli (POSE_MODE=ready ise zorunlu; Mac'te üretildi)
#   <arşiv>/cameras.txt        PINHOLE iç parametreleri (POSE_MODE=colmap'te kullanılır)
# Çıktı: ${OUT_DIR}/${RUN_NAME}_sonuc.tar.gz  (point_cloud.ply, config, dataparser dönüşümü, log, süreler)
# =============================================================================
set -euo pipefail

# ----------------------------- PARAMETRELER ---------------------------------
DATA_ARCHIVE="${DATA_ARCHIVE:-/workspace/in/veri.tar}"   # .tar / .tar.gz / .zip ya da hazır klasör
WORK="${WORK:-/workspace/is}"                             # çalışma klasörü (ağ diski önerilir)
OUT_DIR="${OUT_DIR:-/workspace/out}"
RUN_NAME="${RUN_NAME:-$(date +%Y%m%d-%H%M)_splat}"
POSE_MODE="${POSE_MODE:-ready}"          # ready = Mac'te hazırlanan sparse/0 ; colmap = pod'da COLMAP
COLMAP_MATCHER="${COLMAP_MATCHER:-sequential}"   # sequential (video) | exhaustive (küçük set)
METHOD="${METHOD:-splatfacto}"           # splatfacto | splatfacto-big
MAX_ITERS="${MAX_ITERS:-30000}"
DOWNSCALE="${DOWNSCALE:-1}"              # 1 = tam çözünürlük, 2 = yarı (hızlı deneme)
KEEP_COORDS="${KEEP_COORDS:-1}"          # 1 = nerfstudio'nun yönlendirme/merkezleme/ölçeklemesini kapat (COLMAP koordinatları korunur; bayrak adları doğrulanmadı)
NS_VERSION="${NS_VERSION:-}"             # boş = pip'teki son sürüm; ör. "==1.1.5" ile sabitle
PIP_EXTRA="${PIP_EXTRA:-}"
DRY_RUN="${DRY_RUN:-0}"
# ----------------------------------------------------------------------------

LOG_DIR="${WORK}/log"
T0=$(date +%s)
declare -a TIMES=()

say()  { printf '\n[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
run()  { echo "+ $*"; if [[ "${DRY_RUN}" != "1" ]]; then "$@"; fi; }
step_done() { local now; now=$(date +%s); TIMES+=("$1=$((now - T_STEP))s"); T_STEP=${now}; }

mkdir -p "${WORK}" "${OUT_DIR}" "${LOG_DIR}"
T_STEP=${T0}

# 0) GPU kontrolü --------------------------------------------------------------
say "0) GPU kontrolü"
if [[ "${DRY_RUN}" != "1" ]]; then
  command -v nvidia-smi >/dev/null || { echo "HATA: nvidia-smi yok — NVIDIA GPU'lu pod gerekli"; exit 1; }
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv | tee "${LOG_DIR}/gpu.txt"
fi
step_done gpu

# 1) Bağımlılıklar ---------------------------------------------------------------
say "1) Bağımlılık kurulumu"
if [[ "${POSE_MODE}" == "colmap" ]]; then
  # Ubuntu deposundaki colmap genelde CUDA'sız derlenir → SIFT CPU'da (yavaş ama çalışır).
  run apt-get update -y
  run apt-get install -y --no-install-recommends colmap
fi
run apt-get install -y --no-install-recommends unzip pigz || true
run python3 -m pip install --upgrade pip
# shellcheck disable=SC2086
run python3 -m pip install "nerfstudio${NS_VERSION}" ${PIP_EXTRA}
run python3 -c "import torch; assert torch.cuda.is_available(), 'CUDA yok'; print('torch', torch.__version__, torch.cuda.get_device_name(0))"
step_done kurulum

# 2) Veri ----------------------------------------------------------------------------
say "2) Veriyi aç: ${DATA_ARCHIVE}"
DATA="${WORK}/veri"
mkdir -p "${DATA}"
if [[ -d "${DATA_ARCHIVE}" ]]; then
  run rsync -a "${DATA_ARCHIVE}/" "${DATA}/"
else
  case "${DATA_ARCHIVE}" in
    *.tar.gz|*.tgz) run tar -xzf "${DATA_ARCHIVE}" -C "${DATA}" ;;
    *.tar)          run tar -xf  "${DATA_ARCHIVE}" -C "${DATA}" ;;
    *.zip)          run unzip -q "${DATA_ARCHIVE}" -d "${DATA}" ;;
    *) echo "HATA: bilinmeyen arşiv türü: ${DATA_ARCHIVE}"; exit 1 ;;
  esac
fi
# Arşiv tek üst klasör içeriyorsa içine gir
if [[ "${DRY_RUN}" != "1" && ! -d "${DATA}/images" ]]; then
  sub=$(find "${DATA}" -mindepth 2 -maxdepth 2 -type d -name images | head -n1)
  [[ -n "${sub}" ]] && DATA=$(dirname "${sub}")
  [[ -d "${DATA}/images" ]] || { echo "HATA: images/ bulunamadı"; exit 1; }
fi
if [[ "${DRY_RUN}" != "1" ]]; then
  NIMG=$(find "${DATA}/images" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.png' \) | wc -l)
  echo "Görüntü sayısı: ${NIMG}" | tee "${LOG_DIR}/veri.txt"
fi
step_done veri

# 3) Poz -----------------------------------------------------------------------------
say "3) Poz (POSE_MODE=${POSE_MODE})"
if [[ "${POSE_MODE}" == "colmap" ]]; then
  CAM_ARGS=()
  if [[ -f "${DATA}/cameras.txt" ]]; then
    read -r _ _ _ _ FX FY CX CY < <(grep -v '^#' "${DATA}/cameras.txt" | head -n1)
    CAM_ARGS=(--ImageReader.camera_params "${FX},${FY},${CX},${CY}")
  fi
  run colmap feature_extractor --database_path "${DATA}/db.db" --image_path "${DATA}/images" \
      --ImageReader.camera_model PINHOLE --ImageReader.single_camera 1 "${CAM_ARGS[@]}"
  if [[ "${COLMAP_MATCHER}" == "exhaustive" ]]; then
    run colmap exhaustive_matcher --database_path "${DATA}/db.db"
  else
    run colmap sequential_matcher --database_path "${DATA}/db.db" --SequentialMatching.overlap 20
  fi
  run mkdir -p "${DATA}/sparse"
  run colmap mapper --database_path "${DATA}/db.db" --image_path "${DATA}/images" --output_path "${DATA}/sparse" \
      --Mapper.ba_refine_focal_length 0 --Mapper.ba_refine_principal_point 0
elif [[ "${POSE_MODE}" == "ready" ]]; then
  [[ "${DRY_RUN}" == "1" || -d "${DATA}/sparse/0" ]] || { echo "HATA: ${DATA}/sparse/0 yok (POSE_MODE=ready)"; exit 1; }
else
  echo "HATA: POSE_MODE ready|colmap olmalı"; exit 1
fi
NS_DATA="${WORK}/ns_data"
run ns-process-data images --data "${DATA}/images" --output-dir "${NS_DATA}" \
    --skip-colmap --skip-image-processing --colmap-model-path "${DATA}/sparse/0"
step_done poz

# 4) Eğitim --------------------------------------------------------------------------
say "4) Eğitim: ${METHOD}, ${MAX_ITERS} adım, downscale ${DOWNSCALE}"
PARSER_ARGS=(nerfstudio-data --downscale-factor "${DOWNSCALE}")
if [[ "${KEEP_COORDS}" == "1" ]]; then
  PARSER_ARGS+=(--orientation-method none --center-method none --auto-scale-poses False)
fi
run ns-train "${METHOD}" --data "${NS_DATA}" --output-dir "${WORK}/outputs" \
    --experiment-name "${RUN_NAME}" --timestamp egitim \
    --max-num-iterations "${MAX_ITERS}" --viewer.quit-on-train-completion True \
    --logging.local-writer.enable True "${PARSER_ARGS[@]}" 2>&1 | tee "${LOG_DIR}/egitim.log"
step_done egitim

# 5) Dışa aktarım ------------------------------------------------------------------
say "5) .ply dışa aktarımı"
CFG="${WORK}/outputs/${RUN_NAME}/${METHOD}/egitim/config.yml"
EXP="${WORK}/export"
run ns-export gaussian-splat --load-config "${CFG}" --output-dir "${EXP}"
step_done disa_aktarim

# 6) Arşiv ---------------------------------------------------------------------------
say "6) Sonuç arşivi"
PKG="${WORK}/paket/${RUN_NAME}"
run mkdir -p "${PKG}"
run cp -r "${EXP}/." "${PKG}/"
run cp "${CFG}" "${PKG}/config.yml"
run cp "${WORK}/outputs/${RUN_NAME}/${METHOD}/egitim/dataparser_transforms.json" "${PKG}/" || true
run cp -r "${LOG_DIR}" "${PKG}/log"
TOTAL=$(( $(date +%s) - T0 ))
{
  echo "run=${RUN_NAME} method=${METHOD} iters=${MAX_ITERS} downscale=${DOWNSCALE} pose=${POSE_MODE}"
  echo "sureler: ${TIMES[*]} toplam=${TOTAL}s"
} | tee "${LOG_DIR}/ozet.txt"
[[ "${DRY_RUN}" == "1" ]] || cp "${LOG_DIR}/ozet.txt" "${PKG}/"
run tar -C "${WORK}/paket" -czf "${OUT_DIR}/${RUN_NAME}_sonuc.tar.gz" "${RUN_NAME}"
say "BİTTİ → ${OUT_DIR}/${RUN_NAME}_sonuc.tar.gz  (pod'u KAPATMAYI unutmayın: saniye başı ücretlenir)"
