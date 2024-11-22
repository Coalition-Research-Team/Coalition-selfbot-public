# Navigate to the submodule directory
cd python_toxxer_msg_classification

# Fetch and pull the latest changes in the submodule
git fetch
git checkout main
git pull origin main

# Go back to the parent repository
cd ..

# Stage and commit the updated submodule reference
git add .
git commit -m "Updated python_toxxer submodule to latest commit"

# Push the changes in the parent repository
git push origin main
