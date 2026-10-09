"""Classical cryptographic inventory scoring and migration planning."""
from pathlib import Path
import pandas as pd

VULNERABILITY = {
    'RSA': 50, 'RSA-2048': 50, 'RSA-3072': 50, 'ECDSA': 50, 'ECDSA P-256': 50,
    'ECDH': 50, 'ECDH P-256': 50, 'Ed25519': 50, 'DH': 50, 'DSA': 50,
    '3DES': 40, 'DES': 40, 'RC4': 40, 'MD5': 40, 'SHA-1': 40,
    'AES-128': 20, 'AES-256': 0, 'ChaCha20': 0, 'SHA-256': 0, 'SHA-3': 0,
    'ML-KEM': 0, 'ML-DSA': 0,
}
SENSITIVITY = {'Low': 5, 'Medium': 12, 'High': 18, 'Critical': 25}
LIFESPAN = {'Less than 1 year': 0, '1-5 years': 8, '5-10 years': 16, '10+ years': 25}
PUBLIC_KEY = {'RSA-2048','RSA-3072','ECDH P-256','ECDSA P-256','Ed25519','DH','DSA'}
LONG_LIVED = {'5-10 years','10+ years'}


def vulnerability_score(algorithm):
    if algorithm in VULNERABILITY:
        return VULNERABILITY[algorithm]
    for key, value in VULNERABILITY.items():
        if algorithm.startswith(key):
            return value
    raise KeyError(f'Unknown algorithm: {algorithm}')


def migration_for(row):
    alg, usage = row['algorithm'], row['usage']
    if alg in {'RSA-2048','RSA-3072','ECDH P-256','DH'} and usage in {'TLS/HTTPS','VPN','SSH','Email'}:
        return 'ML-KEM-768 (FIPS 203) in hybrid mode', 'Medium'
    if alg in {'RSA-2048','RSA-3072','ECDSA P-256','Ed25519','DSA'} and usage in {'Code Signing','Digital Signatures','API Tokens/JWT'}:
        return 'ML-DSA (FIPS 204); SLH-DSA (FIPS 205) for long-lived firmware', 'High'
    if alg == 'AES-128': return 'AES-256', 'Low'
    if alg in {'3DES','DES','RC4'}: return 'AES-256-GCM', 'Low'
    if alg in {'MD5','SHA-1'}: return 'SHA-256 or SHA-3', 'Low'
    return 'No action', 'None'


def score_inventory(input_path='data/raw/inventory.csv', output_dir='results/tables'):
    df = pd.read_csv(input_path)
    rows = []
    for _, row in df.iterrows():
        vuln = vulnerability_score(row['algorithm'])
        score = 0 if vuln == 0 else min(100, vuln + SENSITIVITY[row['sensitivity']] + LIFESPAN[row['lifespan']])
        level = 'Safe' if vuln == 0 else ('Critical' if score >= 80 else 'High' if score >= 60 else 'Medium' if score >= 40 else 'Low')
        hndl = bool(row['algorithm'] in PUBLIC_KEY and row['usage'] in {'TLS/HTTPS','VPN','SSH','Email'} and row['lifespan'] in LONG_LIVED)
        migration, effort = migration_for(row)
        phase = 'Phase 1 (0-6 months)' if level in {'Critical','High'} else 'Phase 2 (6-18 months)' if level == 'Medium' else 'Phase 3 (18-36 months)'
        rows.append({**row.to_dict(), 'vulnerability_score':vuln, 'risk_score':score, 'risk_level':level, 'HNDL':hndl, 'migration':migration, 'migration_effort':effort, 'phase':phase})
    scored = pd.DataFrame(rows)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out/'inventory_scored.csv', index=False)
    plan_cols = ['asset_name','algorithm','usage','risk_level','HNDL','migration','migration_effort','phase']
    scored[plan_cols].to_csv(out/'migration_plan.csv', index=False)
    return scored
