HACKING
-------


Debug with pydev
~~~~~~~~~~~~~~~~

.. code-block:: python

        import sys
        sys.path.append('/opt/pycharm-4.5/debug-eggs/pycharm-debug.egg')
        import pydevd
        pydevd.settrace('localhost',
                        port=6666,
                        stdoutToServer=True,
                        stderrToServer=True)