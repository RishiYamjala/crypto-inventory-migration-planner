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
KEY_EXCHANGE = {'RSA-2048', 'RSA-3072', 'ECDH P-256', 'DH'}
SIGNATURE = {'RSA-2048', 'RSA-3072', 'ECDSA P-256', 'Ed25519', 'DSA'}
SYMMETRIC = {'AES-128', 'AES-256', '3DES', 'DES', 'RC4', 'ChaCha20'}
HASHING = {'MD5', 'SHA-1', 'SHA-256', 'SHA-3'}


def vulnerability_score(algorithm):
    if algorithm in VULNERABILITY:
        return VULNERABILITY[algorithm]
    for key, value in VULNERABILITY.items():
        if algorithm.startswith(key):
            return value
    raise KeyError(f'Unknown algorithm: {algorithm}')


def algorithm_role(algorithm, usage):
    """Classify the asset's cryptographic role for explainable scoring."""
    if algorithm in KEY_EXCHANGE and algorithm not in {'RSA-2048', 'RSA-3072'}:
        return 'Key exchange / public-key transport'
    if algorithm in {'RSA-2048', 'RSA-3072'}:
        if usage == 'TLS/HTTPS':
            return 'Certificate signature plus possible key transport; role review required'
        if usage in {'Code Signing', 'Digital Signatures', 'API Tokens/JWT'}:
            return 'Digital signature / authentication'
        return 'Public-key use; cryptographic role requires confirmation'
    if algorithm in SIGNATURE or usage in {'Code Signing', 'Digital Signatures', 'API Tokens/JWT'}:
        return 'Digital signature / authentication'
    if algorithm in PUBLIC_KEY:
        return 'Public-key use; cryptographic role requires confirmation'
    if algorithm in SYMMETRIC:
        return 'Symmetric encryption'
    if algorithm in HASHING:
        return 'Hashing / integrity'
    return 'Other cryptographic use'


def threat_rationale(algorithm, usage, lifespan):
    """Explain the lookup result without treating every non-PQC asset equally."""
    if algorithm in {'ECDH P-256', 'DH'}:
        return ('Shor-risk public-key primitive; observed use and confidentiality/signature '
                f'lifetime are {usage} and {lifespan}.')
    if algorithm in {'RSA-2048', 'RSA-3072'}:
        return ('RSA is a dual-use public-key primitive; this inventory does not prove whether '
                f'{usage} uses it for key transport or signatures. Confirm the role before selecting ML-KEM or ML-DSA.')
    if algorithm in {'ECDSA P-256', 'Ed25519', 'DSA'}:
        return f'Shor-risk signature/authentication primitive; observed use and asset lifetime are {usage} and {lifespan}.'
    if algorithm in {'3DES', 'DES', 'RC4', 'MD5', 'SHA-1'}:
        return 'Legacy or collision/strength-weakened primitive; replacement is recommended independently of quantum risk.'
    if algorithm == 'AES-128':
        return 'Symmetric primitive receives a Grover-adjusted score; AES-256 is the recommended upgrade.'
    if algorithm in {'AES-256', 'ChaCha20', 'SHA-256', 'SHA-3', 'ML-KEM', 'ML-DSA'}:
        return 'No quantum vulnerability assigned by this lookup table; continue normal lifecycle and implementation review.'
    return 'No matching rule; validate this asset against the Challenge Kit or organizational policy.'


def migration_for(row):
    alg, usage = row['algorithm'], row['usage']
    if alg in {'RSA-2048', 'RSA-3072'} and usage == 'TLS/HTTPS' and 'certificate' in row['asset_name'].lower():
        return 'ML-KEM-768 (FIPS 203) hybrid key exchange + ML-DSA (FIPS 204) certificate signatures', 'High'
    if alg in {'ECDH P-256','DH'} and usage in {'TLS/HTTPS','VPN','SSH','Email'}:
        return 'ML-KEM-768 (FIPS 203) in hybrid mode', 'Medium'
    if alg in {'RSA-2048','RSA-3072'} and usage in {'VPN','SSH','Email'}:
        return 'Confirm RSA role: ML-KEM for key establishment or ML-DSA for signatures', 'High'
    if alg in {'RSA-2048','RSA-3072','ECDSA P-256','Ed25519','DSA'} and usage in {'Code Signing','Digital Signatures','API Tokens/JWT'}:
        return 'ML-DSA (FIPS 204); SLH-DSA (FIPS 205) for long-lived firmware', 'High'
    if alg in {'ECDSA P-256', 'Ed25519'} and usage == 'SSH':
        return 'ML-DSA (FIPS 204) for authentication/signatures; assess ML-KEM for key exchange', 'High'
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
        rows.append({**row.to_dict(), 'cryptographic_role':algorithm_role(row['algorithm'], row['usage']),
                     'vulnerability_score':vuln, 'risk_score':score, 'risk_level':level, 'HNDL':hndl,
                     'risk_rationale':threat_rationale(row['algorithm'], row['usage'], row['lifespan']),
                     'migration':migration, 'migration_effort':effort, 'phase':phase})
    scored = pd.DataFrame(rows)
    phase_order = {'Phase 1 (0-6 months)': 1, 'Phase 2 (6-18 months)': 2, 'Phase 3 (18-36 months)': 3}
    scored['_sort_key'] = scored.apply(lambda r: (phase_order[r['phase']], -int(r['risk_score']), r['asset_name']), axis=1)
    scored = scored.sort_values('_sort_key').drop(columns='_sort_key').reset_index(drop=True)
    scored.insert(0, 'priority_rank', range(1, len(scored) + 1))
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out/'inventory_scored.csv', index=False)
    plan_cols = ['priority_rank','asset_name','algorithm','cryptographic_role','usage','risk_level','risk_score','HNDL','risk_rationale','migration','migration_effort','phase']
    scored[plan_cols].to_csv(out/'migration_plan.csv', index=False)
    return scored
