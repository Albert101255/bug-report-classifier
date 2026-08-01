# Apply this upgrade

This archive mirrors repository paths. Copy its contents over the root of `Albert101255/bug-report-classifier`, review the diff, then run:

```bash
cp .env.example .env
# Replace all placeholder values in .env
python -m pip install -r requirements.txt -r requirements-dev.txt
python scripts/train_baseline.py
PYTHONPATH=backend pytest backend/tests -q
docker compose config --quiet
```

Suggested Git workflow:

```bash
git switch -c fix/real-baseline-and-security
git add .
git commit -m "Replace simulated classifier with reproducible TF-IDF baseline"
git push -u origin fix/real-baseline-and-security
```

Do not commit `.env` or any access token.
