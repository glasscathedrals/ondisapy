import csv
import math
import os
import sys
import tkinter as tk
import warnings
from itertools import chain
from tkinter import filedialog, messagebox

import cmocean.cm as cmo
import geopandas as gpd
import ipywidgets as widgets
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely.speedups
from cmocean import *
from IPython.display import HTML, display
from ipywidgets import Button, HBox, Layout, VBox
from matplotlib import ticker
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from shapely.ops import cascaded_union

sys.path.insert(0, os.path.join(os.path.dirname(os.getcwd()), 'scripts'))
from windroses import *

warnings.simplefilter("ignore")
shapely.speedups.enable()


class WidgetsMain(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        create_project_button = widgets.Button(description='Criar projeto', tooltip='Cria um novo projeto', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        create_project_button.on_click(self.create_project_button_click)
        load_project_button = widgets.Button(description='Importar projeto', tooltip='Importa o .csv de um projeto criado', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        load_project_button.on_click(self.load_project_button_click)
        project_accordion = widgets.Accordion(
            children=[create_project_button, load_project_button])
        project_accordion.set_title(0, 'Criar projeto')
        project_accordion.set_title(1, 'Importar projeto')
        load_grid_button = widgets.Button(description='Importar .shp de malha processada', tooltip='Importa um .shp que teve sua malha processada', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        load_grid_button.on_click(self.load_grid_button_click)
        shapefile_accordion = widgets.Accordion(children=[load_grid_button])
        shapefile_accordion.set_title(0, 'Importar .shp de malha processada')
        tab_contents = ['Projetos', 'Shapefiles']
        tab_children = [project_accordion, shapefile_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        return tab

    def create_project_button_click(self, b):

        self.project_dirs = self.create_project()

        return self.project_dirs

    def create_project(self):

        if not os.path.exists(os.path.join(self.path, 'proj')):

            os.makedirs(os.path.join(self.path, 'proj'))

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        create_project_asksaveasfilename_dir = filedialog.asksaveasfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Insira o nome desejado para seu projeto:", filetypes=[("Nome do projeto", ".")])

        if create_project_asksaveasfilename_dir == '':

            messagebox.showwarning("ondisapy", "Nenhum projeto criado.")

            return None

        else:

            if not os.path.exists(create_project_asksaveasfilename_dir):

                os.makedirs(create_project_asksaveasfilename_dir)

            project_data_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'data').replace('\\', '/'))
            project_waves_dir = (os.path.join(
                project_data_dir, 'wind_waves').replace('\\', '/'))
            project_winds_dir = (os.path.join(
                project_data_dir, 'wind_data').replace('\\', '/'))
            project_wind_fetchs_dir = (os.path.join(
                project_data_dir, 'wind_fetchs').replace('\\', '/'))
            project_img_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'img').replace('\\', '/'))
            project_grid_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'grid').replace('\\', '/'))
            project_dirs_list = [project_data_dir, project_waves_dir, project_winds_dir,
                                 project_wind_fetchs_dir, project_img_dir, project_grid_dir]

            print("Diretórios de projeto criados:")

            for i in project_dirs_list:

                try:

                    os.makedirs(i)

                    print("%s" % i)

                except OSError as Error:

                    if os.path.exists(i):

                        print("%s já existe." % i)

            project_file_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'dir.csv').replace('\\', '/'))

            if not os.path.exists(project_file_dir):

                project_name = os.path.basename(
                    create_project_asksaveasfilename_dir)
                project_dirs_list.append(project_name)
                project_dirs_dataframe = pd.DataFrame(
                    data={"dir": project_dirs_list})
                project_dirs_dataframe.to_csv(
                    project_file_dir, sep='\t', index=False, header=True, encoding='utf-8')

                messagebox.showinfo(
                    "ondisapy", "Projeto criado com sucesso:\n%s" % project_file_dir)

                print("\nProjeto criado:\n%s\n" % project_file_dir)

                return project_dirs_dataframe

            else:

                print("%s já existe.\n" % project_file_dir)

            print("\n")

    def load_project_button_click(self, b):

        self.project_dirs = self.load_project()

        return self.project_dirs

    def load_project(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_project_askopenfilename_dir = filedialog.askopenfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Confirme o diretório de importação do arquivo '.csv' do seu projeto:", filetypes=[(".csv", "*.csv")])

        if load_project_askopenfilename_dir == '':

            messagebox.showwarning("ondisapy", "Nenhum projeto importado.")

            return None

        else:

            if not ('dir.csv') in str(load_project_askopenfilename_dir):

                messagebox.showwarning(
                    "ondisapy", "Erro: arquivo inválido.\nO arquivo realmente é um .csv de projeto criado?")

                return None

            else:

                project_dirs_dataframe = pd.read_csv(
                    load_project_askopenfilename_dir, sep='\t', engine='python', header=0, encoding='utf-8')

                messagebox.showinfo(
                    "ondisapy", "Projeto importado com sucesso:\n%s" % load_project_askopenfilename_dir)

                print("Projeto importado:\n%s\n" %
                      load_project_askopenfilename_dir)

            return (project_dirs_dataframe)

    def load_grid_button_click(self, b):

        self.grid = self.load_grid()

        return self.grid

    def load_grid(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_grid_askopenfilename_dir = filedialog.askopenfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Confirme o diretório de importação do arquivo '.shp' da sua malha processada", filetypes=[('.shp', '*.shp')])

        if load_grid_askopenfilename_dir == '':

            messagebox.showwarning(
                "ondisapy", "Nenhuma malha processada importada.")

            return None

        else:

            grid_geodataframe = gpd.GeoDataFrame.from_file(
                load_grid_askopenfilename_dir)
            grid_geodataframe = grid_geodataframe.geometry
            grid_geodataframe = gpd.GeoDataFrame(geometry=grid_geodataframe)

            if len(grid_geodataframe.geometry) == 1:

                messagebox.showwarning(
                    "ondisapy", "Erro: shapefile com geometria única.\nEste .shp realmente foi processado?")

                return None

            else:

                grid_geodataframe_areas_list = []

                for i in range(len(grid_geodataframe['geometry'])):

                    grid_geodataframe_area = grid_geodataframe['geometry'][i].area
                    grid_geodataframe_areas_list.append(grid_geodataframe_area)

                grid_geodataframe_size_index = grid_geodataframe_areas_list.index(
                    max(grid_geodataframe_areas_list))
                grid_geodataframe_size_polygon = grid_geodataframe[
                    'geometry'][grid_geodataframe_size_index]
                grid_geodataframe_size = round(
                    (grid_geodataframe_size_polygon.bounds[2]-grid_geodataframe_size_polygon.bounds[0]), 0)
                grid_geodataframe_centroids = grid_geodataframe.centroid
                grid_geodataframe_polygons = [grid_geodataframe['geometry'][:][i] for i in range(
                    len(grid_geodataframe['geometry']))]
                grid_geodataframe_overlay = gpd.GeoSeries(
                    cascaded_union(grid_geodataframe_polygons))
                grid_geodataframe_overlay = grid_geodataframe_overlay[0]
                grid_geodataframe_overlay = gpd.GeoDataFrame(
                    {'geometry': grid_geodataframe_overlay}, index=[0], crs=grid_geodataframe.crs)
                grid_geodataframe_boundary = grid_geodataframe_overlay.boundary
                grid_geodataframe_name = os.path.basename(
                    load_grid_askopenfilename_dir)
                grid_geodataframe_name = os.path.splitext(
                    grid_geodataframe_name)[0]
                grid_geodataframe_datum = grid_geodataframe.crs['init']

                messagebox.showinfo(
                    "ondisapy", "Malha processada importada com sucesso:\n%s" % load_grid_askopenfilename_dir)

                print("Malha processada importada:\n%s\n" %
                      load_grid_askopenfilename_dir)

                return grid_geodataframe_boundary, grid_geodataframe_centroids.reset_index(drop=True), grid_geodataframe_size, grid_geodataframe.reset_index(drop=True), grid_geodataframe_datum, grid_geodataframe_overlay, grid_geodataframe_name


class WidgetsWindWaves(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        cmap_list = ['viridis', 'plasma', 'inferno', 'magma', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic', 'Pastel1', 'Pastel2',
                     'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar', 'cmo.thermal', 'cmo.haline', 'cmo.solar', 'cmo.ice',  'cmo.gray', 'cmo.oxy', 'cmo.deep', 'cmo.dense',  'cmo.algae', 'cmo.matter', 'cmo.turbid', 'cmo.speed', 'cmo.amp', 'cmo.tempo', 'cmo.phase', 'cmo.balance', 'cmo.delta', 'cmo.curl']
        self.wave_heights_cmap_dropdown = widgets.Dropdown(description='Seleção:', options=sorted(
            cmap_list, key=str.lower), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='cmo.ice')
        self.wave_periods_cmap_dropdown = widgets.Dropdown(description='Seleção:', options=sorted(
            cmap_list, key=str.lower), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='cmo.speed')
        self.wave_energies_cmap_dropdown = widgets.Dropdown(description='Seleção:', options=sorted(
            cmap_list, key=str.lower), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='cmo.thermal')
        load_wind_fetchs_button = widgets.Button(description='Importar pistas de vento processada(s)',
                                                 tooltip='Importa pistas de vento processada(s)', layout=Layout(width='30%'), style={'description_width': 'initial'})
        load_wind_fetchs_button.on_click(self.load_wind_fetchs_button_click)
        self.wind_duration_float_text = widgets.FloatText(description='Duração (h):', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.gravity_float_text = widgets.FloatText(
            description='Gravidade: (m/s²)', value=9.81, layout=Layout(width='30%'), style={'description_width': 'initial'})
        self.wind_speed_float_text = widgets.FloatText(
            description='Velocidade (m/s):', layout=Layout(width='30%'), style={'description_width': 'initial'})
        wind_parameters_accordion = widgets.Accordion(
            children=[self.wind_duration_float_text, self.gravity_float_text, self.wind_speed_float_text])
        wind_parameters_accordion.set_title(0, 'Duração do vento (h)')
        wind_parameters_accordion.set_title(1, 'Gravidade (m/s²)')
        wind_parameters_accordion.set_title(2, 'Velocidade do vento (m/s)')
        wave_heights_method_list = ['SMB', 'JONSWAP']
        wave_periods_method_list = ['SMB', 'JONSWAP']
        wave_energies_method_list = ['SMB', 'JONSWAP']
        self.wave_heights_method_dropdown = widgets.Dropdown(description='Método:', options=sorted(
            wave_heights_method_list), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='JONSWAP')
        self.wave_heights_bins_int_text = widgets.IntText(value=10, description='Intervalos:', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.wave_periods_method_dropdown = widgets.Dropdown(description='Método:', options=sorted(
            wave_periods_method_list), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='JONSWAP')
        self.wave_periods_bins_int_text = widgets.IntText(value=10, description='Intervalos:', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.wave_energies_method_dropdown = widgets.Dropdown(description='Método:', options=sorted(
            wave_energies_method_list), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='JONSWAP')
        self.wave_energies_bins_int_text = widgets.IntText(
            value=10, description='Intervalos:', layout=Layout(width='30%'), style={'description_width': 'initial'})
        wave_heights_method_accordion = widgets.Accordion(
            children=[self.wave_heights_method_dropdown, self.wave_heights_cmap_dropdown, self.wave_heights_bins_int_text])
        wave_heights_method_accordion.set_title(
            0, 'Método de cálculo para as alturas de ondas')
        wave_heights_method_accordion.set_title(1, 'Esquema de cores')
        wave_heights_method_accordion.set_title(2, 'Intervalos')
        wave_periods_method_accordion = widgets.Accordion(
            children=[self.wave_periods_method_dropdown, self.wave_periods_cmap_dropdown, self.wave_periods_bins_int_text])
        wave_periods_method_accordion.set_title(
            0, 'Método de cálculo para os períodos de ondas')
        wave_periods_method_accordion.set_title(1, 'Esquema de cores')
        wave_periods_method_accordion.set_title(2, 'Intervalos')
        wave_energies_method_accordion = widgets.Accordion(
            children=[self.wave_energies_method_dropdown, self.wave_energies_cmap_dropdown, self.wave_energies_bins_int_text])
        wave_energies_method_accordion.set_title(
            0, 'Método de cálculo para as energias de ondas')
        wave_energies_method_accordion.set_title(1, 'Esquema de cores')
        wave_energies_method_accordion.set_title(2, 'Intervalos')
        wind_fetchs_accordion = widgets.Accordion(
            children=[load_wind_fetchs_button])
        wind_fetchs_accordion.set_title(0, 'Escolha da(s) pistas de vento')
        tab_contents = ['Pistas de Vento', 'Parâmetros',
                        'Alturas de Ondas', 'Períodos de Ondas', 'Energias de Ondas']
        tab_children = [wind_fetchs_accordion, wind_parameters_accordion,
                        wave_heights_method_accordion, wave_periods_method_accordion, wave_energies_method_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        display(tab)

    def load_wind_fetchs_button_click(self, b):

        self.load_wind_fetchs()

    def load_wind_fetchs(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_wind_fetchs_askopenfilenames_dirs = filedialog.askopenfilenames(initialdir=os.path.join(
            self.path, 'proj'), title="Confirme o diretório de importação do arquivo '.csv' da(s) direção(ões) processada(s):", filetypes=[(".csv", "*.csv")])

        if load_wind_fetchs_askopenfilenames_dirs == '':

            messagebox.showwarning(
                "ondisapy", "Nenhum arquivo de pistas de vento importado.")

        else:

            if not ('wind_fetchs') in str(load_wind_fetchs_askopenfilenames_dirs):

                messagebox.showwarning(
                    "ondisapy", "Erro: arquivo(s) de pistas de vento inválido(s).")

                return None

            else:

                wind_fetchs_list = []

                for i in root.splitlist(load_wind_fetchs_askopenfilenames_dirs):

                    wind_fetchs_list.append(
                        [pd.read_csv(i, sep=';', engine='python', header=None, encoding='utf-8'), i])

                print('\nSelecione a(s) direção(ões) processada(s) desejada(s):')

                wind_directions_list = sorted([i[0].loc[0, [4]].values.tolist()[
                                              0] for i in chain(wind_fetchs_list)])
                self.wind_fetchs_dirs = [i[1] for i in chain(wind_fetchs_list)]
                self.str_wind_directions_list = [
                    (str(i)+'°') for i in wind_directions_list]
                self.wind_directions_select_multiple = widgets.SelectMultiple(
                    options=self.str_wind_directions_list)

                display(self.wind_directions_select_multiple)

    def jonswap(self, wind_fetch, gravity, wind_speed, wind_duration):

        wind_fetch_kilometers = wind_fetch/1000

        if wind_duration > 1.167*((wind_fetch_kilometers**0.7)/(wind_speed**0.4)):

            if wind_fetch_kilometers < 2.32*(wind_speed**2):

                wave_height_value = 0.0163 * \
                    (wind_fetch_kilometers**0.5)*(wind_speed)
                wave_period_value = 0.439 * \
                    (wind_fetch_kilometers**0.3)*(wind_speed**0.4)
                wave_energy_value = (1/8)*gravity*1000*(wave_height_value**2)

                return wave_height_value, wave_period_value, wave_energy_value

            elif wind_fetch_kilometers > 2.32*(wind_speed**2):

                wave_height_value = 0.0248*(wind_speed**2)
                wave_period_value = 0.566*(wind_speed)
                wave_energy_value = (1/8)*gravity*1000*(wave_height_value**2)

                return wave_height_value, wave_period_value, wave_energy_value

        elif wind_duration < 1.167*((wind_fetch_kilometers**0.7)/(wind_speed**0.4)):

            if wind_duration < 2.01*wind_speed:

                wave_height_value = 0.0146 * \
                    (wind_duration**(5/7))*(wind_speed**(9/7))
                wave_period_value = 0.419 * \
                    (wind_duration**(3/7))*(wind_speed**(4/7))
                wave_energy_value = (1/8)*gravity*1000*(wave_height_value**2)

                return wave_height_value, wave_period_value, wave_energy_value

            elif wind_duration > 2.01*wind_speed:

                wave_height_value = 0.0240*(wind_speed**2)
                wave_period_value = 0.566*(wind_speed)
                wave_energy_value = (1/8)*gravity*1000*(wave_height_value**2)

                return wave_height_value, wave_period_value, wave_energy_value

    def smb(self, wind_fetch, gravity, wind_speed):

        wave_height_kk = 0.0125*(((gravity*wind_fetch)/(wind_speed**2))**0.42)
        wave_height_tan_hiper = (math.exp(wave_height_kk)-math.exp(-wave_height_kk))/(
            math.exp(wave_height_kk)+math.exp(-wave_height_kk))
        wave_height_value = 0.283*(wind_speed**2/gravity)*wave_height_tan_hiper
        wave_period_kk = 0.077*(((gravity*wind_fetch)/(wind_speed**2))**0.25)
        wave_period_tan_hiper = (math.exp(wave_period_kk)-math.exp(-wave_period_kk))/(
            math.exp(wave_period_kk)+math.exp(-wave_period_kk))
        wave_period_value = 1.20 * \
            (wind_speed*2*np.pi/gravity)*wave_period_tan_hiper
        wave_energy_value = (1/8)*gravity*1000*(wave_height_value**2)

        return wave_height_value, wave_period_value, wave_energy_value

    def outputs(self, grid, project_dirs):

        self.grid = grid
        self.project_dirs = project_dirs

        for i in self.wind_directions_select_multiple.value:

            wind_fetchs_dir = self.wind_fetchs_dirs[self.str_wind_directions_list.index(
                i)]
            wind_fetchs_dataframe = pd.read_csv(
                wind_fetchs_dir, sep=';', engine='python', header=None, encoding='utf-8')
            x_centroids_list = wind_fetchs_dataframe.loc[:, 1].values.tolist()
            y_centroids_list = wind_fetchs_dataframe.loc[:, 2].values.tolist()
            wind_fetchs_list = wind_fetchs_dataframe.loc[:, 3].values.tolist()
            wind_direction = wind_fetchs_dataframe.loc[0, [4]].tolist()[0]
            wind_fetchs_method = wind_fetchs_dataframe.loc[0, [5]].tolist()[0]
            wind_waves_dataframe = wind_fetchs_dataframe[[0, 1, 2, 4, 3, 5]]

            if self.wave_heights_method_dropdown.value == 'JONSWAP':

                wave_heights_list = [self.jonswap(j, self.gravity_float_text.value, self.wind_speed_float_text.value, self.wind_duration_float_text.value)[
                    0] for j in wind_waves_dataframe[3]]
                wave_heights_method = 'jonswap'

            elif self.wave_heights_method_dropdown.value == 'SMB':

                wave_heights_list = [self.smb(j, self.wind_speed_float_text.value, self.gravity_float_text.value)[
                    0] for j in wind_waves_dataframe[3]]
                wave_heights_method = 'smb'

            if self.wave_periods_method_dropdown.value == 'JONSWAP':

                wave_periods_list = [self.jonswap(j, self.gravity_float_text.value, self.wind_speed_float_text.value, self.wind_duration_float_text.value)[
                    1] for j in wind_waves_dataframe[3]]
                wave_periods_method = 'jonswap'

            elif self.wave_periods_method_dropdown.value == 'SMB':

                wave_periods_list = [self.smb(j, self.gravity_float_text.value, self.wind_speed_float_text.value)[
                    1] for j in wind_waves_dataframe[3]]
                wave_periods_method = 'smb'

            if self.wave_energies_method_dropdown.value == 'JONSWAP':

                wave_energies_list = [self.jonswap(j, self.gravity_float_text.value, self.wind_speed_float_text.value, self.wind_duration_float_text.value)[
                    2] for j in wind_waves_dataframe[3]]
                wave_energies_method = 'jonswap'

            elif self.wave_energies_method_dropdown.value == 'SMB':

                wave_energies_list = [self.smb(j, self.gravity_float_text.value, self.wind_speed_float_text.value)[
                    2] for j in wind_waves_dataframe[3]]
                wave_energies_method = 'smb'

            wind_waves_dataframe = wind_waves_dataframe.drop(0, axis=1)
            wind_waves_dataframe = wind_waves_dataframe.rename(
                columns={1: 'x', 2: 'y', 3: 'wind_fetchs', 4: 'wind_direction', 5: 'wind_fetchs_method'})
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'wind_duration'] = self.wind_duration_float_text.value
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'wind_speed'] = self.wind_speed_float_text.value
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'gravity'] = self.gravity_float_text.value
            wind_waves_dataframe['wave_heights'] = wave_heights_list
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'wave_heights_method'] = wave_heights_method
            wind_waves_dataframe['wave_periods'] = wave_periods_list
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'wave_periods_method'] = wave_periods_method
            wind_waves_dataframe['wave_energies'] = wave_energies_list
            wind_waves_dataframe.loc[wind_waves_dataframe.index[0],
                                     'wave_energies_method'] = wave_energies_method
            wind_waves_dataframe = wind_waves_dataframe.fillna(value='')
            wind_waves_outputs_dirs = os.path.join(
                self.project_dirs['dir'][1], self.grid[6]).replace('\\', '/')

            try:

                os.makedirs(wind_waves_outputs_dirs)

            except OSError as Error:

                if os.path.exists(wind_waves_outputs_dirs):

                    pass

            if wind_fetchs_method == 'saville':

                wind_waves_dataframe.to_csv(os.path.join(wind_waves_outputs_dirs, self.grid[6]+'_'+str(wind_fetchs_method)+'_'+str(wind_direction).replace('.', '_')+'_'+str(
                    self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

                display(wind_waves_dataframe)

                print("\nDados salvos em:\n%s\n" % os.path.join(wind_waves_outputs_dirs, self.grid[6]+'_'+str(wind_fetchs_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.csv').replace('\\', '/'))

            elif wind_fetchs_method == 'spm':

                wind_waves_dataframe.to_csv(os.path.join(wind_waves_outputs_dirs, self.grid[6]+'_'+str(wind_fetchs_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

                display(wind_waves_dataframe)

                print("\nDados salvos em:\n%s\n" % os.path.join(wind_waves_outputs_dirs, self.grid[6]+'_'+str(wind_fetchs_method)+'_'+str(
                    wind_direction).replace('.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.csv').replace('\\', '/'))

            figure, axes = plt.subplots(figsize=(15, 15))
            self.grid[3]['wave_heights'] = wind_waves_dataframe['wave_heights']
            self.grid[3].plot(column='wave_heights', cmap=self.wave_heights_cmap_dropdown.value, ax=axes, antialiased=True, snap=True, scheme='equal_interval', k=self.wave_heights_bins_int_text.value,
                              legend=True, legend_kwds={'loc': 'lower right', 'fontsize': 8, 'edgecolor': 'black', 'fancybox': False, 'title': 'Intervalos (m)', 'title_fontsize': '8'})
            self.grid[0].plot(ax=axes, color='black', linewidth=0.5)
            axes_scalebar_font_properties = FontProperties(size=8)
            axes_scalebar = AnchoredSizeBar(axes.transData, 1000, '1.0 km', loc=3, pad=0.5, color='black',
                                            frameon=True, borderpad=0.5, sep=5, fontproperties=axes_scalebar_font_properties)
            axes.add_artist(axes_scalebar)
            axes.set_axisbelow(True)
            axes.margins(0.2, 0.2)
            axes.grid(color='lightgrey', linewidth=0.5,
                      linestyle='-', alpha=0.5)
            windrose_axes = figure.add_axes(
                [0, 0, 0.07, 0.07], projection='windrose')
            windrose_var = [1]
            windrose_wind_direction = [wind_direction]
            windrose_dataframe = pd.DataFrame(
                {'bearing': windrose_wind_direction, 'var': windrose_var})
            windrose_axes.bar(windrose_dataframe['bearing'], windrose_dataframe['var'],
                              normed=False, opening=4, bins=1, edgecolor='k', colors='white', nsector=128)
            windrose_axes.set_yticklabels([])
            windrose_ticks = np.arange(0, 360, 45)
            windrose_axes.set_thetagrids(
                windrose_ticks, fontsize=6, ha='center', va='center')
            windrose_axes.tick_params(direction='in', pad=0)
            axes_position = axes.get_position()
            windrose_axes_position = windrose_axes.get_position()
            windrose_axes.set_position([(axes_position.x1-windrose_axes_position.width)-(windrose_axes_position.width*0.1)-(0.75*windrose_axes_position.width*0.1), (axes_position.y1 -
                                                                                                                                                                     windrose_axes_position.height)-(windrose_axes_position.height*0.1)-(windrose_axes_position.height*0.1), windrose_axes_position.width, windrose_axes_position.height])
            wave_heights_method = wind_waves_dataframe['wave_heights_method'][0]
            wind_direction = wind_waves_dataframe['wind_direction'][0]

            if wave_heights_method == 'jonswap':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nDuração: %.2f h\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['wind_duration'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            elif wave_heights_method == 'smb':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            wind_waves_heights_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], self.grid[6], 'wind_waves', 'wind_waves_heights').replace('\\', '/')

            try:

                os.makedirs(wind_waves_heights_outputs_dir)

            except OSError as Error:

                if os.path.exists(wind_waves_heights_outputs_dir):

                    pass

            if wind_fetchs_method == 'saville':

                plt.savefig(os.path.join(wind_waves_heights_outputs_dir, self.grid[6]+'_'+str(wave_heights_method)+'_'+str(wind_direction).replace('.', '_')+'_'+str(
                    self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_heights_outputs_dir, self.grid[6]+'_'+str(wave_heights_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))

            elif wind_fetchs_method == 'spm':

                plt.savefig(os.path.join(wind_waves_heights_outputs_dir, self.grid[6]+'_'+str(wave_heights_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_heights_outputs_dir, self.grid[6]+'_'+str(wave_heights_method)+'_'+str(
                    wind_direction).replace('.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))

            figure, axes = plt.subplots(figsize=(15, 15))
            self.grid[3]['wave_periods'] = wind_waves_dataframe['wave_periods']
            self.grid[3].plot(column='wave_periods', cmap=self.wave_periods_cmap_dropdown.value, ax=axes, antialiased=True, snap=True, scheme='equal_interval', k=self.wave_periods_bins_int_text.value,
                              legend=True, legend_kwds={'loc': 'lower right', 'fontsize': 8, 'edgecolor': 'black', 'fancybox': False, 'title': 'Intervalos (s)', 'title_fontsize': '8'})
            self.grid[0].plot(ax=axes, color='black', linewidth=0.5)
            axes_scalebar_font_properties = FontProperties(size=8)
            axes_scalebar = AnchoredSizeBar(axes.transData, 1000, '1.0 km', loc=3, pad=0.5, color='black',
                                            frameon=True, borderpad=0.5, sep=5, fontproperties=axes_scalebar_font_properties)
            axes.add_artist(axes_scalebar)
            axes.set_axisbelow(True)
            axes.margins(0.2, 0.2)
            axes.grid(color='lightgrey', linewidth=0.5,
                      linestyle='-', alpha=0.5)
            windrose_axes = figure.add_axes(
                [0, 0, 0.07, 0.07], projection='windrose')
            windrose_var = [1]
            windrose_wind_direction = [wind_direction]
            windrose_dataframe = pd.DataFrame(
                {'bearing': windrose_wind_direction, 'var': windrose_var})
            windrose_axes.bar(windrose_dataframe['bearing'], windrose_dataframe['var'],
                              normed=False, opening=4, bins=1, edgecolor='k', colors='white', nsector=128)
            windrose_axes.set_yticklabels([])
            windrose_ticks = np.arange(0, 360, 45)
            windrose_axes.set_thetagrids(
                windrose_ticks, fontsize=6, ha='center', va='center')
            windrose_axes.tick_params(direction='in', pad=0)
            axes_position = axes.get_position()
            windrose_axes_position = windrose_axes.get_position()
            windrose_axes.set_position([(axes_position.x1-windrose_axes_position.width)-(windrose_axes_position.width*0.1)-(0.75*windrose_axes_position.width*0.1), (axes_position.y1 -
                                                                                                                                                                     windrose_axes_position.height)-(windrose_axes_position.height*0.1)-(windrose_axes_position.height*0.1), windrose_axes_position.width, windrose_axes_position.height])
            wave_periods_method = wind_waves_dataframe['wave_periods_method'][0]
            wind_direction = wind_waves_dataframe['wind_direction'][0]

            if wave_periods_method == 'jonswap':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nDuração: %.2f h\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['wind_duration'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            elif wave_periods_method == 'smb':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            wind_waves_periods_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], self.grid[6], 'wind_waves', 'wind_waves_periods').replace('\\', '/')

            try:

                os.makedirs(wind_waves_periods_outputs_dir)

            except OSError as Error:

                if os.path.exists(wind_waves_periods_outputs_dir):

                    pass

            if wind_fetchs_method == 'saville':

                plt.savefig(os.path.join(wind_waves_periods_outputs_dir, self.grid[6]+'_'+str(wave_periods_method)+'_'+str(wind_direction).replace('.', '_')+'_'+str(
                    self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_periods_outputs_dir, self.grid[6]+'_'+str(wave_periods_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))

            elif wind_fetchs_method == 'spm':

                plt.savefig(os.path.join(wind_waves_periods_outputs_dir, self.grid[6]+'_'+str(wave_periods_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_periods_outputs_dir, self.grid[6]+'_'+str(wave_periods_method)+'_'+str(
                    wind_direction).replace('.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))

            figure, axes = plt.subplots(figsize=(15, 15))
            self.grid[3]['wave_energies'] = wind_waves_dataframe['wave_energies']
            self.grid[3].plot(column='wave_energies', cmap=self.wave_energies_cmap_dropdown.value, ax=axes, antialiased=True, snap=True, scheme='equal_interval', k=self.wave_energies_bins_int_text.value,
                              legend=True, legend_kwds={'loc': 'lower right', 'fontsize': 8, 'edgecolor': 'black', 'fancybox': False, 'title': 'Intervalos (J/m²)', 'title_fontsize': '8'})
            self.grid[0].plot(ax=axes, color='black', linewidth=0.5)
            axes_scalebar_font_properties = FontProperties(size=8)
            axes_scalebar = AnchoredSizeBar(axes.transData, 1000, '1.0 km', loc=3, pad=0.5, color='black',
                                            frameon=True, borderpad=0.5, sep=5, fontproperties=axes_scalebar_font_properties)
            axes.add_artist(axes_scalebar)
            axes.set_axisbelow(True)
            axes.margins(0.2, 0.2)
            axes.grid(color='lightgrey', linewidth=0.5,
                      linestyle='-', alpha=0.5)
            windrose_axes = figure.add_axes(
                [0, 0, 0.07, 0.07], projection='windrose')
            windrose_var = [1]
            windrose_wind_direction = [wind_direction]
            windrose_dataframe = pd.DataFrame(
                {'bearing': windrose_wind_direction, 'var': windrose_var})
            windrose_axes.bar(windrose_dataframe['bearing'], windrose_dataframe['var'],
                              normed=False, opening=4, bins=1, edgecolor='k', colors='white', nsector=128)
            windrose_axes.set_yticklabels([])
            windrose_ticks = np.arange(0, 360, 45)
            windrose_axes.set_thetagrids(
                windrose_ticks, fontsize=6, ha='center', va='center')
            windrose_axes.tick_params(direction='in', pad=0)
            axes_position = axes.get_position()
            windrose_axes_position = windrose_axes.get_position()
            windrose_axes.set_position([(axes_position.x1-windrose_axes_position.width)-(windrose_axes_position.width*0.1)-(0.75*windrose_axes_position.width*0.1), (axes_position.y1 -
                                                                                                                                                                     windrose_axes_position.height)-(windrose_axes_position.height*0.1)-(windrose_axes_position.height*0.1), windrose_axes_position.width, windrose_axes_position.height])
            wave_energies_method = wind_waves_dataframe['wave_energies_method'][0]
            wind_direction = wind_waves_dataframe['wind_direction'][0]

            if wave_energies_method == 'jonswap':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nDuração: %.2f h\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['wind_duration'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            elif wave_energies_method == 'smb':

                axes_anchored_text = AnchoredText('Velocidade: %.2f m/s\nGravidade: %.2f m/s²' % (
                    wind_waves_dataframe['wind_speed'][0], wind_waves_dataframe['gravity'][0]), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
                axes.add_artist(axes_anchored_text)

            wind_waves_energies_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], self.grid[6], 'wind_waves', 'wind_waves_energies').replace('\\', '/')

            try:

                os.makedirs(wind_waves_energies_outputs_dir)

            except OSError as Error:

                if os.path.exists(wind_waves_energies_outputs_dir):

                    pass

            if wind_fetchs_method == 'saville':

                plt.savefig(os.path.join(wind_waves_energies_outputs_dir, self.grid[6]+'_'+str(wave_energies_method)+'_'+str(wind_direction).replace('.', '_')+'_'+str(
                    self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_energies_outputs_dir, self.grid[6]+'_'+str(wave_energies_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'_'+str(self.wind_duration_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))

            elif wind_fetchs_method == 'spm':

                plt.savefig(os.path.join(wind_waves_energies_outputs_dir, self.grid[6]+'_'+str(wave_energies_method)+'_'+str(wind_direction).replace(
                    '.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
                plt.show()

                print("\nImagem salva em:\n%s\n" % os.path.join(wind_waves_energies_outputs_dir, self.grid[6]+'_'+str(wave_energies_method)+'_'+str(
                    wind_direction).replace('.', '_')+'_'+str(self.wind_speed_float_text.value).replace('.', '_')+'.png').replace('\\', '/'))
