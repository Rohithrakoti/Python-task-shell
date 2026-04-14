# --- Step 2: Compare repos in batches (FIXED)

print(f"\n🔍 Comparing repos using {MAX_WORKERS} parallel workers...\n")

results: list[RepoSyncResult] = []

START_INDEX = int(os.getenv("START_INDEX", 0))
END_INDEX = int(os.getenv("END_INDEX", 10))

# ✅ MUST exist before batch loop
selected_repos = org1_repos[START_INDEX:END_INDEX]

print(f"Processing repos from {START_INDEX} to {END_INDEX}")

# ✅ Batch size (important for disk issue)
BATCH_SIZE = 5

with IncrementalResultWriter() as writer:

    for i in range(0, len(selected_repos), BATCH_SIZE):
        batch = selected_repos[i:i + BATCH_SIZE]

        print(f"\n📦 Processing batch {i // BATCH_SIZE + 1}")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {}

            for repo in batch:
                repo_name = repo["name"]
                org2_repo_id = org2_lookup.get(repo_name.lower())

                # ✅ HANDLE missing repo in org2
                if not org2_repo_id:
                    missing_result = RepoSyncResult(
                        repo_name=repo_name,
                        is_synced=False,
                        error="Repository not found in org2"
                    )
                    writer.write(missing_result)
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
                writer.write(result)
                results.append(result)

        # 🔥 VERY IMPORTANT (disk cleanup AFTER EACH BATCH)
        cleanup()

# --- Step 3: Report
print_summary(results)
save_results(results)

out_of_sync_count = sum(1 for r in results if not r.is_synced)
sys.exit(1 if out_of_sync_count > 0 else 0)
