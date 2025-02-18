#!/bin/sh
# activate.sh
# NOTE:
# 1. To debug, run with `DEBUG=Y ./activate.sh`
# 2. $0 in a sourced script gives different values between running in bash and
# zsh. In zsh, $0 always reflects the current script name, while in bash $0
# shows the root level command name that source the scripts (nested, bash
# a.sh->source b.sh->source c.sh, where $0 in c.sh shows "a.sh", or .
# ./a.sh->source b.sh->source c.sh, where $0 in c.sh shows "bash")
# 3. Source this Python virutal environment activation script to launch the
# environment. Usually, you sourcing this script in your project specific
# start script, say run.sh, then there are 2 ways to kick off run.sh:
#  3.1 ./run.sh:
#  + if #!/bin/sh points to bash, then DIR will be ".", the same location
#  where ./run.sh is situated, which means the venv.incl to use or the virtual
#  environment to be activated is of the local project.
#  + if #!/bin/sh points to zsh or #!/bin/zsh, then DIR will be "$RHUB/py",
#  the same location where this script itself is situated, which means the
#  venv.incl to use or the virtual environment to be activated is the common
#  one.
#  3.2 . ./run.sh:
#  + if zsh is the default shell of the terminal, then as per #2 above,
#  sourcing run.sh will activate the common virtual environment which lies in
#  the same place of this script.
# 4. Enable debug: DEBUG=Y . $RHUB/py/activate.sh
#

DEBUG=${DEBUG:-"N"}
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
cd "$SCRIPT_DIR"
# echo $DEBUG
if [ "$DEBUG" = 'Y' ]; then
	echo "\$0=$0"
	echo "DIR=$SCRIPT_DIR"
	echo "source $SCRIPT_DIR/venv.incl"
fi
source ./venv.incl
source $VENV/bin/activate
cd -

# vim: tw=78:ts=8:sts=4:sw=4:ft=sh:norl:
