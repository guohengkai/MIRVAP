from distutils.core import setup
import py2exe

setup(windows=[{"script":"main2.py"}], options={"py2exe":{"includes":["sip", "PyQt4.QtOpenGL", 
	"vtk.vtkRenderingPythonSIP", "vtk.vtkCommonPythonSIP", "vtk.vtkFilteringPythonSIP", "scipy.sparse.csgraph._validation"]}})
#, zipfile=None