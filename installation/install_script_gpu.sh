#!/bin/bash

export http_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"
export https_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"

#export SOFTWARE_HOME=/usr/local/share/software
export SOFTWARE_HOME=/opt/custom
export TMP_DIR=/var/extra/tmp/softwares

echo "y"|sudo yum install java-1.8.0-openjdk-devel gcc gcc-c++ screen p7zip enchant sox maven emacs docker-ce \
    python-devel.x86_64 python27-python-devel.x86_64  python36-devel.x86_64 python-pip python-setuptools dos2unix unix2dos \
    libcurl-devel libxml2-devel openssl-devel cmake bazel cvs git git-lfs
echo "y"|sudo yum group install "Development Tools"
echo "y"|sudo yum install devtoolset-7-gcc*


mkdir -p $TMP_DIR
cd $TMP_DIR

##Gradle
gradle_version=4.10.2
echo "#####Installing gradle version-  $gradle_version"
wget https://services.gradle.org/distributions/gradle-${gradle_version}-bin.zip
unzip gradle-${gradle_version}-bin.zip
mkdir -p $SOFTWARE_HOME/gradle
mv gradle-${gradle_version} $SOFTWARE_HOME/gradle
#adding gradle as an alternative
sudo update-alternatives --install /usr/local/bin/gradle gradle $SOFTWARE_HOME/gradle/gradle-${gradle_version}/bin/gradle 1


##Python - Anaconda installation
cd $TMP_DIR
anaconda_version=5.3.1
## getting anaconda 3
wget https://repo.anaconda.com/archive/Anaconda3-${anaconda_version}-Linux-x86_64.sh
chmod +x Anaconda3-${anaconda_version}-Linux-x86_64.sh
./Anaconda3-${anaconda_version}-Linux-x86_64.sh -b -p $SOFTWARE_HOME/python/anaconda3

###downgrading default python to 3.6 as tensorflow is not yet supported in python=3.7
echo "y" | $SOFTWARE_HOME/python/anaconda3/bin/conda install python=3.6

##installing various packages using pip
##for tensorflow==1.15 gpu support is there in the same package not tensorflow-gpu
$SOFTWARE_HOME/python/anaconda3/bin/pip install \
    virtualenv scikit-learn xgboost lightgbm tensorflow==1.15 tensorflow-hub gensim fbprophet jupyterlab seaborn plotly tqdm argparse wordcloud spacy shiny eli5 \
    jupyter_contrib_nbextensions jupyter_nbextensions_configurator autopep8 pyspark chainer

##chinese tokenization
$SOFTWARE_HOME/python/anaconda3/bin/pip install jieba


#installing torch
#check if new version are available & it is available in pypi
$SOFTWARE_HOME/python/anaconda3/bin/pip install http://download.pytorch.org/whl/cpu/torch-0.4.1-cp36-cp36m-linux_x86_64.whl
$SOFTWARE_HOME/python/anaconda3/bin/pip install torchvision

#other packages from torch ecosystem
$SOFTWARE_HOME/python/anaconda3/bin/pip install allennlp fastai

sudo update-alternatives --install /usr/local/bin/conda conda $SOFTWARE_HOME/python/anaconda3/bin/conda 1
sudo update-alternatives --install /usr/local/bin/python3 python3 $SOFTWARE_HOME/python/anaconda3/bin/python3 1
sudo update-alternatives --install /usr/local/bin/pip3 pip3 $SOFTWARE_HOME/python/anaconda3/bin/pip 1
#adding python 3 virtualenv as the default virtualenv
sudo update-alternatives --install /usr/local/bin/virtualenv virtualenv $SOFTWARE_HOME/python/anaconda3/bin/virtualenv 1
#adding python 3 jupyter notebook as the default option
sudo update-alternatives --install /usr/local/bin/jupyter jupyter $SOFTWARE_HOME/python/anaconda3/bin/jupyter 1


##creating python 2.7 environment
echo "y" | $SOFTWARE_HOME/python/anaconda3/bin/conda create -n py27 anaconda python=2.7
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip install -U pip
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip install -U \
    virtualenv scikit-learn xgboost lightgbm tensorflow tensorflow-hub gensim fbprophet jupyterlab seaborn plotly tqdm argparse wordcloud spacy shiny eli5 \
    jupyter_contrib_nbextensions jupyter_nbextensions_configurator pyspark


#installing torch
#check if new version is available & it is available in pypi
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip install http://download.pytorch.org/whl/cpu/torch-0.4.1-cp27-cp27mu-linux_x86_64.whl
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip install torchvision

#other packages from torch ecosystem
##allennlp not available in python=2.7, it's only available in python 3
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip install fastai

sudo update-alternatives --install /usr/local/bin/python2 python2 $SOFTWARE_HOME/python/anaconda3/envs/py27/bin/python 1
sudo update-alternatives --install /usr/local/bin/pip2 pip2 $SOFTWARE_HOME/python/anaconda3/envs/py27/bin/pip 1
cd /usr/local/bin
ln -s python2 python
ln -s pip2 pip

#installing ipykernel so that py27 is visible from jupyter notebook
#default location is -  /usr/local/share/jupyter/kernels
$SOFTWARE_HOME/python/anaconda3/envs/py27/bin/python -m ipykernel install --name py27 --display-name "Python 2.7 (py27)"


###creating another enviroment for tensorflow 2.0
echo "y" | $SOFTWARE_HOME/python/anaconda3/bin/conda create -n tf2.0 anaconda python=3.7
$SOFTWARE_HOME/python/anaconda3/envs/tf2.0/bin/pip install -U tensorflow-gpu tensorflow-hub

#installing ipykernel so that tf2.0 is visible from jupyter notebook
#default location is -  /usr/local/share/jupyter/kernels
$SOFTWARE_HOME/python/anaconda3/envs/tf2.0/bin/python -m ipykernel install --name tf2.0 --display-name "Python 3.7 - tensorflow 2.0 (tf2.0)"


##Scala
scala_version=2.11.12
mkdir -p $TMP_DIR
cd $TMP_DIR
wget https://downloads.lightbend.com/scala/${scala_version}/scala-${scala_version}.tgz
tar -xzf scala-${scala_version}.tgz
mkdir -p $SOFTWARE_HOME/scala
cp -r scala-${scala_version} $SOFTWARE_HOME/scala/

###Spark
spark_version=2.4.0-bin-hadoop2.7
mkdir -p $TMP_DIR
cd $TMP_DIR
##the url have another ref to spark 2.4
wget http://mirrors.estointernet.in/apache/spark/spark-2.4.0/spark-${spark_version}.tgz
tar -xzf spark-${spark_version}.tgz
mkdir -p $SOFTWARE_HOME/spark
mv spark-${spark_version} $SOFTWARE_HOME/spark
##installing jupyter kernel for spark
export SPARK_HOME=$SOFTWARE_HOME/spark/spark-${spark_version}
export PATH=$PATH:$SPARK_HOME/bin
$SOFTWARE_HOME/python/anaconda3/bin/pip install toree
$SOFTWARE_HOME/python/anaconda3/bin/jupyter toree install --spark_home=$SPARK_HOME --interpreters=Scala,SQL --spark_opts='--master=local[4]'

###Maven custom as the version with centos was older & didn't work with some of our code
maven_version=3.6.0
cd $TMP_DIR
wget mirrors.estointernet.in/apache/maven/maven-3/3.6.0/binaries/apache-maven-${maven_version}-bin.tar.gz
tar -xzf apache-maven-${maven_version}-bin.tar.gz
mkdir -p $SOFTWARE_HOME/maven
mv apache-maven-${maven_version} $SOFTWARE_HOME/maven
rm apache-maven-${maven_version}-bin.tar.gz

# install R packages & jupyter kernel plugin
## for installing prophet rstan was dependency & for current installation had to follow - https://github.com/stan-dev/rstan/issues/569
R -e 'install.packages(c("dplyr","data.table","ggplot2","car","xgboost","tm","forecast","openxlsx","readr","stringr","RJDBC","tidyr","lubridate","shiny","shinydashboard","randomForest","caret","foreach","glmnet","parallel","jsonlite","e1071","nnet","sqldf","caTools","Hmisc","rJava","doParallel","reshape2","gbm","prophet"),repos="http://cran.us.r-project.org")'
R -e 'install.packages(c("IRkernel"),repos="http://cran.us.r-project.org")'
R -e 'IRkernel::installspec(user = FALSE)'

