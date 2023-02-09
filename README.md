# budget_backend

You probably need conda and git to be able to run the following code. You can get conda here:
```
https://docs.conda.io/en/latest/miniconda.html
```
python 3.8 or 3.9 is suggested, decent chance 3.10 might be unstable. Installation instructions:
```
https://docs.conda.io/en/latest/miniconda.html#installing
```
You can verify you conda is installed correctly by opening an new terminal and typing:
```
(base) maz@maz-NUC8i5BEK:~$ which conda
/home/maz/anaconda3/bin/conda
(base) maz@maz-NUC8i5BEK:~$ conda --version
conda 22.9.0
```
Keep in mind that:
```
(base) maz@maz-NUC8i5BEK:~$ 
```
are (NAME_OF_ENV) USER@HOST:~$. This is provided for the easy of debugging any potenatial issues


Git install instructions are here (you should have it by default on Mac and Linux):
```
https://github.com/git-guides/install-git
```
again you should verify you've got git installed:
```
(base) maz@maz-NUC8i5BEK:~$ which git
/usr/bin/git
(base) maz@maz-NUC8i5BEK:~$ git --version
git version 2.25.1
```
If you have conda and git installed you can begin setting up this repository. 
Open new terminal / shell / powershell in your OS and cd to the destination 
where you want your repository to be cloned. Let's say I'm in my main directory:
```
(base) maz@maz-NUC8i5BEK:~$ ls
anaconda3  Desktop  Documents  Downloads  Music  Pictures  Public  snap  Templates  Videos
```
and I want to create a folder called project and clone both repositories there. Now I can
```
(base) maz@maz-NUC8i5BEK:~$ mkdir project
(base) maz@maz-NUC8i5BEK:~$ cd project
(base) maz@maz-NUC8i5BEK:~/project$ 
```
so now I'm in the project folder that's empty. We can use
```
git clone
```
to clone both repositories. You can repo links from github. You can either use https or ssh auth, but the latter is preffered. It might require setting up ssh keys, but instructions are in github docs..
So let's say I cloned two repositories by doing:
```
git clone git@github.com:marekkaras/budget_backend.git
git clone git@github.com:marekkaras/budget_frontend.git
```
if I list files in this folder I should see:
```
(base) maz@maz-NUC8i5BEK:~/project$ ls
budget_backend  budget_frontend
```
let's change directory to backends folder:
```
(base) maz@maz-NUC8i5BEK:~/project$ cd budget_backend/
(base) maz@maz-NUC8i5BEK:~/project/budget_backend$ ls
budget  enviroment.yml  README.md
```
you'll see enviroment.yml here. This is where conda comes handy. You can
```
conda env create --file enviroment.yml
```
which will create virtual env from the file called uni_project. You can verify by:
```
(base) maz@maz-NUC8i5BEK:~/project/budget_backend$ conda env list
# conda environments:
#
base                     /home/maz/anaconda3
uni_project              /home/maz/anaconda3/envs/uni_project
```
now you can:
```
#
# To activate this environment, use
#
#     $ conda activate uni_project
#
# To deactivate an active environment, use
#
#     $ conda deactivate

```
and finally you can start entire back end by running:
```
uvicorn budget.main:app --host 0.0.0.0 --port 8045 --reload
```
keep in mind you need that shell open. You should be able to navigate in your browser to:
```
INFO:     Uvicorn running on http://0.0.0.0:8045 (Press CTRL+C to quit)
```
or more precisely:
```
http://0.0.0.0:8045/docs
```
to see all avilable endpoints.


you can also run below script to generate test user with some random data being populated
```
python generate_test_user.py
```