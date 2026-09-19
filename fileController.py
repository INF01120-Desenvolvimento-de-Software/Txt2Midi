import tkinter as tk
from tkinter import filedialog
from File import txtFile

class fileController:
    
    @staticmethod
    def get_txt_content() -> str:
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo TXT",
            filetypes=[("Text Files", "*.txt")]
        )
        root.destroy()
        
        if file_path:
            try:
                imported_file = txtFile(file_path)
                return imported_file.text
            except Exception as e:
                print(f"Erro ao carregar o arquivo: {e}")
                return None
        
        return None