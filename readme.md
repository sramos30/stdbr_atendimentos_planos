# git clone git@github.com:sramos30/stdbr_atendimentos_planos.git

git clone --single-branch --branch planos_6 git@github.com:sramos30/stdbr_atendimentos_planos.git .

git remote add origin git@github.com:sramos30/stdbr_atendimentos_planos.git

-- rsync -hvar --delete --force --exclude=.git ./planos/ ../phpMsqlPhpadminDocker/www/atendimentos/planos/
python ./hlCopyPlanosDev.py -s ./planos/ -d ../phpMsqlPhpadminDocker/www/atendimentos/planos/

sudo chown -R www-data:www-data ../phpMsqlPhpadminDocker/www/atendimentos/planos/

git init
git add *
git commit -m "fist commit"
git remote add origin git@github.com:sramos30/stdbr_atendimentos_planos.git
git branch -M master
git push -u origin master

# To switch to a branch
> git switch <branch-name>

# To delete a branch

# For a safe deletion (only if the branch has been merged into your current branch):
> git branch -d <branch-name>

# To force deletion (if the branch has unmerged changes you are sure you want to discard):
> git branch -D <branch-name>


# creating a branch 
# Ensure your local main branch is up to date with the remote repository's changes by running:

> git checkout master && git pull origin master

# create and switch to a new branch to store planos from 1 to 3799
> git checkout -b planos_1 
> git push -u origin planos_1

# create and switch to a new branch to store planos from 3800 to 4199
> git checkout -b planos_2
> git push -u origin planos_2

# create and switch to a new branch to store planos from 4200 to 4499
> git checkout -b planos_3
> git push -u origin planos_3

# create and switch to a new branch to store planos from 4500 to 4999
> git checkout -b planos_4
> git push -u origin planos_4

# create and switch to a new branch to store planos from 5000 to 5399
> git checkout -b planos_5
> git push -u origin planos_5

# create and switch to a new branch to store planos from 5400 to 9999
> git checkout -b planos_6
> git push -u origin planos_6

# Create the Multi-Volume Archive to store planos in parts of 50M
tar -cvfz planos_N.tgz planos_1/
split --bytes=50M planos_N.tgz "planos_N.tgz_"

# Combine and Extract the Archive 
cat planos_N.tgz_* > planos_N.tgz

