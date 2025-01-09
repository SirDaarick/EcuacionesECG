#Elaborado por: 
#García Rodríguez Erick Daniel 
#Rodríguez Ramírez Fernanda
#Junco Martinez Bruno Salvador
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftfreq
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Funcion para aplicar filtros
def apply_filter(spectrum, freqs, filter_type, cutoff):
    if filter_type == "low-pass":
        spectrum[np.abs(freqs) > cutoff] = 0
    elif filter_type == "high-pass":
        spectrum[np.abs(freqs) < cutoff] = 0
    return spectrum

# Funcion principal del proyecto
def analyze_ecg(file_path, patient_index, low_cutoff, high_cutoff, sampling_rate=200):
    try:
        # Leer archivo de datos
        data = pd.read_csv(file_path, header=None)
        
        # Validar el indice del paciente
        if patient_index < 0 or patient_index >= len(data):
            messagebox.showerror("Error", "Índice de paciente fuera de rango.")
            return None, None, None
        
        # Extraer la senal y etiqueta del paciente
        signal = data.iloc[patient_index, :-1].values  # Seleccionar la fila del paciente (ignorar la etiqueta)
        label = data.iloc[patient_index, -1]  # ultima columna es la etiqueta (0: normal, 1: anormal)
        n = len(signal)  # Numero de puntos de datos

        # Crear eje de tiempo
        duration = n / sampling_rate  # Duracion total de la senal
        time = np.linspace(0, duration, n, endpoint=False)  # Eje de tiempo en segundos

        # Transformada de Fourier
        spectrum = fft(signal)
        freqs = fftfreq(n, 1 / sampling_rate)
        
        # Aplicar filtro pasa-bajas
        filtered_spectrum = apply_filter(spectrum.copy(), freqs, "low-pass", low_cutoff)
        # Aplicar filtro pasa-altas
        filtered_spectrum = apply_filter(filtered_spectrum, freqs, "high-pass", high_cutoff)
        
        # Reconstruir senal
        filtered_signal = np.real(ifft(filtered_spectrum))

        return time, signal, filtered_signal

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None, None, None

# Interfaz gráfica mejorada 
def main():
    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("Archivo s CSV", "*.csv")])
        if file_path:
            file_path_var.set(file_path)
            load_initial_data()

    def load_initial_data():
        file_path = file_path_var.get()
        try:
            patient_index = int(patient_index_var.get())
            time, signal, filtered_signal = analyze_ecg(file_path, patient_index, low_cutoff_slider.get(), high_cutoff_slider.get())
            if time is not None:
                update_plot(time, signal, filtered_signal)
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un índice de paciente válido.")

    def update_plot(time, signal, filtered_signal):
        ax_original.clear()
        ax_filtered.clear()
        ax_combined.clear()

        ax_original.plot(time, signal, label="Original", color="dodgerblue")
        ax_original.set_title("Señal ECG Original")
        ax_original.set_xlabel("Tiempo (s)")
        ax_original.set_ylabel("Amplitud")
        ax_original.legend()

        ax_filtered.plot(time, filtered_signal, label="Filtrada", color="deeppink")
        ax_filtered.set_title("Señal ECG Filtrada")
        ax_filtered.set_xlabel("Tiempo (s)")
        ax_filtered.set_ylabel("Amplitud")
        ax_filtered.legend()

        ax_combined.plot(time, signal, label="Original", color="dodgerblue")
        ax_combined.plot(time, filtered_signal, label="Filtrada", color="deeppink")
        ax_combined.set_title("Señales Combinadas")
        ax_combined.set_xlabel("Tiempo (s)")
        ax_combined.set_ylabel("Amplitud")
        ax_combined.legend()

        canvas_original.draw()
        canvas_filtered.draw()
        canvas_combined.draw()

    def update_filter(event=None):
        file_path = file_path_var.get()
        try:
            patient_index = int(patient_index_var.get())
            time, signal, filtered_signal = analyze_ecg(file_path, patient_index, low_cutoff_slider.get(), high_cutoff_slider.get())
            if time is not None:
                update_plot(time, signal, filtered_signal)
        except ValueError:
            pass

    # Configuración de la ventana principal
    root = tk.Tk()
    root.title("Análisis de Señales ECG")
    root.geometry("1442x900")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10), padding=5)
    style.configure("TLabel", font=("Arial", 10))

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Archivo de señales ECG:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    file_path_var = tk.StringVar()
    ttk.Entry(frame, textvariable=file_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
    ttk.Button(frame, text="Seleccionar Archivo", command=select_file).grid(row=0, column=2, padx=10, pady=10)

    ttk.Label(frame, text="Índice del paciente:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    patient_index_var = tk.StringVar()
    ttk.Entry(frame, textvariable=patient_index_var).grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(frame, text="Corte pasa-bajas (Hz):").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    low_cutoff_slider = tk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=300, command=update_filter)
    low_cutoff_slider.set(50)
    low_cutoff_slider.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

    ttk.Label(frame, text="Corte pasa-altas (Hz):").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
    high_cutoff_slider = tk.Scale(frame, from_=0, to=5, orient=tk.HORIZONTAL, resolution=0.1, length=300, command=update_filter)
    high_cutoff_slider.set(0.5)
    high_cutoff_slider.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

    # Gráficos de Matplotlib
    fig_original, ax_original = plt.subplots(figsize=(7, 3))
    canvas_original = FigureCanvasTkAgg(fig_original, master=root)
    canvas_widget_original = canvas_original.get_tk_widget()
    canvas_widget_original.grid(row=1, column=0, padx=10, pady=10, sticky=tk.N)

    fig_filtered, ax_filtered = plt.subplots(figsize=(7, 3))
    canvas_filtered = FigureCanvasTkAgg(fig_filtered, master=root)
    canvas_widget_filtered = canvas_filtered.get_tk_widget()
    canvas_widget_filtered.grid(row=2, column=0, padx=10, pady=10, sticky=tk.S)

    fig_combined, ax_combined = plt.subplots(figsize=(7, 6))
    canvas_combined = FigureCanvasTkAgg(fig_combined, master=root)
    canvas_widget_combined = canvas_combined.get_tk_widget()
    canvas_widget_combined.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky=tk.N)

    root.mainloop()

if __name__ == "__main__":
    main()
