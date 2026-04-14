import os

START_INDEX = int(os.getenv("START_INDEX", 0))
END_INDEX = int(os.getenv("END_INDEX", 100))

selected_repos = org1_repos[START_INDEX:END_INDEX]

print(f"Processing repos from {START_INDEX} to {END_INDEX}")

with IncrementalResultWriter() as writer:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}

        for repo in selected_repos:
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

        for future in futures:
            result = future.result()
            writer.write(result)
