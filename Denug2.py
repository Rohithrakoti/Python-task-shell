import os
from concurrent.futures import ThreadPoolExecutor

# Step 2: Compare repos (BATCH CONTROLLED FROM ENV)

print(f"\n🔍 Comparing repos using {MAX_WORKERS} parallel workers...\n")

results = []  # ✅ FIX: must be defined before use

# ✅ Get batch indexes from pipeline (or default)
START_INDEX = int(os.getenv("START_INDEX", 0))
END_INDEX = int(os.getenv("END_INDEX", 50))  # default 50

# ✅ Slice ONLY required repos
selected_repos = org1_repos[START_INDEX:END_INDEX]

print(f"Processing ONLY repos from {START_INDEX} to {END_INDEX}")
print(f"Total selected repos: {len(selected_repos)}")

# ❌ IMPORTANT: NO internal batching loop here

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {}

    for repo in selected_repos:
        repo_name = repo["name"]
        org2_repo_id = org2_lookup.get(repo_name.lower())

        # ✅ Handle missing repo in org2
        if not org2_repo_id:
            missing_result = RepoSyncResult(
                repo_name=repo_name,
                is_synced=False,
                error="Repository not found in org2"
            )
            results.append(missing_result)
            continue

        # ✅ Submit job
        future = executor.submit(
            compare_repo,
            repo_name,
            repo["id"],
            org2_repo_id
        )
        futures[future] = repo_name

    # ✅ Collect results
    for future in futures:
        result = future.result()
        results.append(result)

# ✅ Step 3: Report
print_summary(results)
save_results(results)

# ✅ Exit code
out_of_sync_count = sum(1 for r in results if not r.is_synced)
sys.exit(1 if out_of_sync_count > 0 else 0)
