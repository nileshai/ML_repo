###bashrc file to be used in dsgpool machines - https://247inc.atlassian.net/wiki/spaces/SPSCI/pages/79528955/DSG+Machines+dsg-pool+and+dsg-gpu
##change the name of file to .bashrc when you are copying this file to your home folder

SOFTWARE_HOME=/opt/custom
SOFTWARE_HOME2=/rap/speech_science/software

export HOME2=/data/users/$(whoami)

###Java
export JAVA_HOME=/usr/lib/jvm/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH

##Python anaconda
ANACONDA_HOME=$SOFTWARE_HOME/python/anaconda3
export PATH=$ANACONDA_HOME/bin:$PATH

###Scala
export SCALA_HOME=$SOFTWARE_HOME/scala/scala-2.11.12
export PATH=$PATH:$SCALA_HOME/bin

### Hadoop
export HADOOP_HOME=$SOFTWARE_HOME/hadoop/hadoop-2.7.3
export PATH=$PATH:$HADOOP_HOME/bin

### Hive
export HIVE_HOME=$SOFTWARE_HOME/hive/apache-hive-1.2.1-bin
export PATH=$PATH:$HIVE_HOME/bin

###Spark
#export SPARK_HOME=$SOFTWARE_HOME/spark/spark-2.4.0-bin-hadoop2.7
export SPARK_HOME=$SOFTWARE_HOME/spark/spark-2.4.4-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

###Maven
#export MAVEN_HOME=$SOFTWARE_HOME/maven/apache-maven-3.6.0
export MAVEN_HOME=$SOFTWARE_HOME/maven/apache-maven-3.6.2
export PATH=$MAVEN_HOME/bin:$PATH

##SRILM
#export SRILM_HOME=/rap/slm_tools/srilm-170
#export SRILM_HOME=$SOFTWARE_HOME2/srilm/srilm-1.7.0
export SRILM_HOME=$SOFTWARE_HOME2/srilm/srilm-1.7.1

##Texlive
export TEXLIVE_HOME=/usr/local/texlive/2018
export PATH=$TEXLIVE_HOME/bin/x86_64-linux/:$PATH

export http_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"
export https_proxy="http://proxy-grp1.lb-priv.svc.247-inc.net:3128"

#alias to activate py27 conda environment
alias py27='source activate py27'
alias tf2.0='source activate tf2.0'
#alias tf2.0='conda activate tf2.0'

#deactivate conda environment
alias sd='source deactivate'

#to activate python=2.7 environment (py27) at start uncomment the following
#source activate py27

###alias
alias h='cd $HOME2'
alias cds='cd $SOFTWARE_HOME2'

###### ssh to various machines
alias fafr18='ssh fafr18.swamp.sv2.tellme.com'
alias fafr22='ssh fafr22.swamp.sv2.tellme.com'
alias fafr24='ssh fafr24.pool.sv2.247-inc.net'

alias sd1='ssh dsg-pool01.dev.sv2.247-inc.net'
alias sd2='ssh dsg-pool02.dev.sv2.247-inc.net'
alias sd3='ssh dsg-pool03.dev.sv2.247-inc.net'
alias sd4='ssh dsg-pool04.dev.sv2.247-inc.net'

alias sdp1='ssh dev-praas01.app.shared.int.sv2.247-inc.net'
alias sdp2='ssh dev-praas02.app.shared.int.sv2.247-inc.net'
alias sdp3='ssh dev-praas03.app.shared.int.sv2.247-inc.net'
alias sarb1='ssh dev-dsg-clientnode01.hadoop.int.sv2.247-inc.net'

## prod machines
alias sg='ssh dsg-gpu01.bigdata.va1.247-inc.net'
alias sa1='ssh analysis01.sandbox.bigdata.va1.247-inc.net'
alias sa2='ssh analysis02.sandbox.bigdata.va1.247-inc.net'
alias sa3='ssh jgeorge@analysis03.sandbox.bigdata.va1.247-inc.net'
alias sa4='ssh jgeorge@analysis04.sandbox.bigdata.va1.247-inc.net'
alias sa5='ssh jgeorge@analysis05.sandbox.bigdata.va1.247-inc.net'
alias sa6='ssh jgeorge@analysis06.sandbox.bigdata.va1.247-inc.net'
