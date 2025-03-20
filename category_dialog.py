from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
from file_category import FileCategory


class CategoryDialog(QDialog):
    """Dialog for adding or editing file categories"""
    def __init__(self, category=None, parent=None):
        super().__init__(parent)
        self.category = category or FileCategory("New Category")
        self.setWindowTitle("Edit Category" if category else "Add Category")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()

        # Category name
        self.name_edit = QLineEdit(self.category.name)
        form_layout.addRow("Category Name:", self.name_edit)

        # Extensions
        self.extensions_edit = QLineEdit(", ".join(self.category.extensions))
        form_layout.addRow("Extensions (comma separated):", self.extensions_edit)

        # Color (simplified for now)
        self.color_combo = QComboBox()

        # TODO => Add color picker and centralize the colors list in one place
        colors = [
            ("Blue", "#3498db"), ("Red", "#e74c3c"), 
            ("Green", "#2ecc71"), ("Purple", "#9b59b6"),
            ("Orange", "#e67e22"), ("Yellow", "#f39c12"),
            ("Gray", "#34495e"), ("Teal", "#1abc9c")
        ]
        
        for name, code in colors:
            self.color_combo.addItem(name, code)
            
        # Set current color if it matches any in our list
        for i, (name, code) in enumerate(colors):
            if code.lower() == self.category.color.lower():
                self.color_combo.setCurrentIndex(i)
                break
                
        form_layout.addRow("Color:", self.color_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setMinimumWidth(400)
    
    def accept(self):
        # Update category with new values
        self.category.name = self.name_edit.text().strip()
        extensions = [ext.strip() for ext in self.extensions_edit.text().split(",")]
        self.category.extensions = [ext for ext in extensions if ext]
        self.category.color = self.color_combo.currentData()
        
        super().accept()

    def reject(self):
        super().reject()
