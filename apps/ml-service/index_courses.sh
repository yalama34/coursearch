echo "Running course index"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

cd "$SCRIPT_DIR" || exit 1

python -m scripts.index_courses

if [ $? -eq 0 ]; then
  echo "Course index completed successfully."
  exit 0
else
  echo "Course index failed."
  exit 1
fi