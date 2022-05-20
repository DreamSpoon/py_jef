# py_jef addon for Blender
Additional Python 'Run Script' buttons for Blender, in many places.
Helps with addon creation by saving code that was run, it's output (print() statements, stdout), and any exceptions that occurred.
Run Text objects as scripts.

TODO:
- buttons in every possible Tools location (shader editor, graph editor, etc.)
- save output of code to text objects, and these Text objects are parented to the object they created... or the other way around
- auto-run Textblocks / Text objects when frame is changed - to allow scripts to have parent objects, and actions occur as parent object changes state
  - e.g. automatically create sparks when a Rigid Body object changes movement direction
