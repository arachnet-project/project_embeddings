    git filter-repo --path wrk/.bash_profile --path wrk/x --invert-paths

This rewrites the entire history removing those files from every commit.

After that you need to force push since the history has been rewritten:

    git push origin main --force

Then add wrk/ to .gitignore immediately to prevent this happening again:

    echo "wrk/" >> .gitignore
    git add .gitignore
    git commit -m "chore: add wrk/ to .gitignore"
    git push

Is the repository on GitHub or somewhere else? If it is a private repository on GitHub you should also check the GitHub secret scanning alerts in the repository security settings, as GitHub may have already detected the exposed key.

