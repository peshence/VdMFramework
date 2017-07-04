export ROOTSYS=/nfshome0/lumipro/brilconda/root:/afs/cern.ch/cms/lumi/brilconda-1.1.7/root
export PATH=$ROOTSYS/bin:$PATH
export LD_LIBRARY_PATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/root/lib:/nfshome0/lumipro/brilconda/root/lib:/nfshome0/lumipro/brilconda/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/root/lib:$PWD:$PWD/fits:$PWD/corrections:/nfshome0/lumipro/brilconda/root/lib:/nfshome0/lumipro/brilconda/lib:$PYTHONPATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH
export PYTHONPATH=${PWD}:$PYTHONPATH
export PYTHONPATH=${PWD}/fits:$PYTHONPATH
export PYTHONPATH=${PWD}/corrections:$PYTHONPATH
export VDMPATH=${PWD}
export PATH=/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:/nfshome0/lumipro/brilconda/bin:$PATH
#source /afs/cern.ch/cms/lumi/brilconda-1.1.7/root/bin/thisroot.sh
#echo "Is your username listed in remote list?"
#echo
#git remote -v
#echo
#echo "If not, do 'git remote add YOURGITUSERNAME git@github.com:YOURGITUSERNAME/VdMFramework.git'."
unset ROOTSYS