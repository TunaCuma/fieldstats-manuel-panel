from PyQt6.QtCore import QObject, pyqtSignal

class Detachable(QObject):
    """Interface for components that can be detached to a separate window"""
    detached = pyqtSignal()
    reattached = pyqtSignal()
    
    def detach(self):
        """Detach component to a separate window"""
        raise NotImplementedError("Subclasses must implement detach()")
    
    def reattach(self):
        """Reattach component from separate window"""
        raise NotImplementedError("Subclasses must implement reattach()")
