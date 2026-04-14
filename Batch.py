BATCH_SIZE = 100

for i in range(0, len(org1_repos), BATCH_SIZE):
    batch = org1_repos[i:i + BATCH_SIZE]
    print(f"Processing batch {i//BATCH_SIZE + 1}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}

        for repo in batch:
            repo_name = repo["name"]
            org2_repo_id = org2_lookup.get(repo_name.lower())

            if not org2_repo_id:
                missing_result = RepoSyncResult(
                    repo_name=repo_name,
                    is_synced=False,
                    error="Repository not found in org2"
                )
                writer.write(missing_result)
                continue

            future = executor.submit(
                compare_repo,
                repo_name,
                repo["id"],
                org2_repo_id
            )
            futures[future] = repo_name

        # collect results
        for future in futures:
            result = future.result()
            writer.write(result)

    # cleanup after each batch
    import gc
    gc.collect()
