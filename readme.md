# git clone git@github.com:sramos30/stdbr_atendimentos_planos.git

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

