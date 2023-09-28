from datasketch import MinHash, MinHashLSH
from tqdm import tqdm
import time

# set1 = set(['minhash', 'is', 'a', 'probabilistic', 'data', 'structure', 'for',
#             'estimating', 'the', 'similarity', 'between', 'datasets'])
# set2 = set(['minhash', 'is', 'a', 'probability', 'data', 'structure', 'for',
#             'estimating', 'the', 'similarity', 'between', 'documents'])
# set3 = set(['minhash', 'is', 'probability', 'data', 'structure', 'for',
#             'estimating', 'the', 'similarity', 'between', 'documents'])

# m1 = MinHash(num_perm=128)
# m2 = MinHash(num_perm=128)
# m3 = MinHash(num_perm=128)
# for d in set1:
#     m1.update(d.encode('utf8'))
# for d in set2:
#     m2.update(d.encode('utf8'))
# for d in set3:
#     m3.update(d.encode('utf8'))

# Create LSH index
lsh = MinHashLSH(params=[20, 450], num_perm=9000)
# lsh.insert("m2", m2)
# lsh.insert("m3", m3)
# result = lsh.query(m1)
# print("Approximate neighbours with Jaccard similarity > 0.5", result)

eng_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_sr/GoURMET/eng_Latn-srp_Latn/GoURMET.eng_Latn"
srp_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_sr/GoURMET/eng_Latn-srp_Latn/GoURMET.srp_Latn"

eng_lines = []
with open(eng_path, 'r') as f:
    for line in f:
        eng_lines.append(line)

srp_lines = []
with open(srp_path, 'r') as f:
    for line in f:
        srp_lines.append(line)

for i, (srp_line, eng_line) in enumerate(tqdm(zip(srp_lines, eng_lines), total=len(srp_lines))):
    srp_line = srp_line.strip()
    eng_line = eng_line.strip()
    mh = MinHash(num_perm=9000)
    for word in (srp_line + " " + eng_line).split():
        mh.update(word.encode('utf8'))
    lsh.insert(f'{str(i).zfill(6)}', mh)


ts = time.time()
for i, (srp_line, eng_line) in enumerate(zip(srp_lines, eng_lines)):
    srp_line = srp_line.strip()
    eng_line = eng_line.strip()
    mh = MinHash(num_perm=9000)
    for word in (srp_line + " " + eng_line).split():
        mh.update(word.encode('utf8'))
    result = lsh.query(mh)
    if len(result) > 1:
        print(f'{i+1} has duplicates on lines {[int(el)+1 for el in result if int(el) != i]}')

print(f'Time elapsed: {time.time() - ts}')