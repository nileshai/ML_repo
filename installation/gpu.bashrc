###bashrc file to be used in gpu machine - https://247inc.atlassian.net/wiki/spaces/SPSCI/pages/79528955/DSG+Machines+dsg-pool+and+dsg-gpu
##change the name of file to .bashrc when you are copying this file to your home folder

export SOFTWARE_HOME=/opt/custom
#SOFTWARE_HOME=/usr/local/share/software

###Java
export JAVA_HOME=/usr/lib/jvm/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH

##Python anaconda
ANACONDA_HOME=$SOFTWARE_HOME/python/anaconda3
export PATH=$ANACONDA_HOME/bin:$PATH

###Scala
export SCALA_HOME=$SOFTWARE_HOME/scala/scala-2.11.12
export PATH=$PATH:$SCALA_HOME/bin

###Spark
export SPARK_HOME=$SOFTWARE_HOME/spark/spark-2.4.0-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

###Maven
export MAVEN_HOME=$SOFTWARE_HOME/maven/apache-maven-3.6.0
export PATH=$MAVEN_HOME/bin:$PATH

export http_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"
export https_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"

##CUDA

#for cuda support
##CUDA version 9.0, 10.0 are installed on this machine
export CUDA_VERSION=9.0
export CUDA_HOME=/usr/local/cuda-${CUDA_VERSION}                                                                                                                                                     >
export PATH=/usr/local/cuda-${CUDA_VERSION}/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-${CUDA_VERSION}/lib64:${LD_LIBRARY_PATH}:/usr/local/cuda-${CUDA_VERSION}/extras/CUPTI/lib64/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH


##for tensorrt support, https://docs.nvidia.com/deeplearning/sdk/tensorrt-install-guide/index.html
export TENSORRT_HOME=$SOFTWARE_HOME/tensorrt/TensorRT-5.0.2.6
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$TENSORRT_HOME:/lib

##to switch to main working directory
alias h='cd /var/extra/users/$USER/'
alias h2='cd /space/users/$USER/'

alias sa1='ssh jgeorge@analysis01.sandbox.bigdata.va1.247-inc.net'
alias sa2='ssh jgeorge@analysis02.sandbox.bigdata.va1.247-inc.net'
alias sa3='ssh jgeorge@analysis03.sandbox.bigdata.va1.247-inc.net'
alias sa4='ssh jgeorge@analysis04.sandbox.bigdata.va1.247-inc.net'
alias sa5='ssh jgeorge@analysis05.sandbox.bigdata.va1.247-inc.net'
alias sa6='ssh jgeorge@analysis06.sandbox.bigdata.va1.247-inc.net'

#alias to activate py27 conda environment
alias py27='source activate py27'
alias tf2.0='source activate tf2.0'
#alias tf2.0='conda activate tf2.0'

#deactivate conda environment
alias sd='source deactivate'

#to activate python=2.7 environment (py27) at start uncomment the following
#source activate py27

##get gpu utilization
alias topg='watch -n 1 nvidia-smi'

