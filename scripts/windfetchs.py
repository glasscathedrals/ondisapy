import csv
import itertools
import math
import os
import re
import sys
import tkinter as tk
import warnings
from itertools import chain
from math import ceil
from random import randint
from tkinter import filedialog, messagebox

import cmocean.cm as cmo
import geopandas as gpd
import ipywidgets as widgets
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import shapely.speedups
from cmocean import *
from IPython.display import HTML, display
from ipywidgets import Button, FloatProgress, HBox, Layout, VBox
from matplotlib import ticker
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from shapely.geometry import (
    LinearRing, LineString, MultiPolygon, Point, Polygon)
from shapely.ops import cascaded_union, unary_union

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
        load_shapefile_button = widgets.Button(description='Importar .shp', tooltip='Importa um .shp para processamento', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        load_shapefile_button.on_click(self.load_shapefile_button_click)
        load_grid_button = widgets.Button(description='Importar .shp de malha processada', tooltip='Importa um .shp que teve sua malha processada', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        load_grid_button.on_click(self.load_grid_button_click)
        shapefile_accordion = widgets.Accordion(
            children=[load_shapefile_button, load_grid_button])
        shapefile_accordion.set_title(0, 'Importar .shp')
        shapefile_accordion.set_title(1, 'Importar .shp de malha processada')
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

    def load_shapefile_button_click(self, b):

        self.shapefile = self.load_shapefile()

        return self.shapefile

    def load_shapefile(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_shapefile_askopenfilename_dir = filedialog.askopenfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Confirme o diretório de importação do arquivo '.shp' do seu projeto:", filetypes=[('.shp', '*.shp')])

        if load_shapefile_askopenfilename_dir == '':

            messagebox.showwarning("ondisapy", "Nenhum shapefile importado.")

            return None

        else:

            shp_geodataframe = gpd.GeoDataFrame.from_file(
                load_shapefile_askopenfilename_dir)
            shp_geodataframe = shp_geodataframe.geometry
            shp_geodataframe = gpd.GeoDataFrame(geometry=shp_geodataframe)

            if len(shp_geodataframe.geometry) != 1:

                messagebox.showwarning(
                    "ondisapy", "Erro: shapefile com mais de uma geometria.")

                return None

            else:

                epsg_dict = {'init': ('epsg:32718', 'epsg:32719', 'epsg:32720',
                                      'epsg:32721', 'epsg:32722', 'epsg:32723', 'epsg:32724', 'epsg:32725')}

                if shp_geodataframe.crs['init'] in epsg_dict['init']:

                    shp_geodataframe_datum = shp_geodataframe.crs['init']

                    messagebox.showinfo(
                        "ondisapy", "Shapefile importado com sucesso:\n%s" % load_shapefile_askopenfilename_dir)

                    print("Shapefile importado:\n%s\n" %
                          load_shapefile_askopenfilename_dir)

                    return shp_geodataframe, shp_geodataframe_datum

                else:

                    messagebox.showwarning(
                        "ondisapy", "Erro: o shapefile importado não está contido em um dos EPSGs aceitos.\nPor favor, geoprocesse sua geometria novamente.")

                    return None

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


class WidgetsGrid(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        self.grid_size_float_text = widgets.FloatText(description='Malha (m):', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        grid_size_accordion = widgets.Accordion(
            children=[self.grid_size_float_text])
        grid_size_accordion.set_title(
            0, 'Dimensão da malha quadriculada a ser processada')
        tab_contents = ['Malha']
        tab_children = [grid_size_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        return tab

    def create_grid(self, shapefile, grid_size, cut=True):

        self.shapefile = shapefile
        self.grid_size = grid_size
        self.cut = cut

        x_min, y_min = [i.min() for i in self.shapefile.bounds.T.values[:2]]
        x_max, y_max = [i.max() for i in self.shapefile.bounds.T.values[2:]]
        x_ceil = ceil((x_max-x_min)/self.grid_size)
        y_ceil = ceil((y_max-y_min)/self.grid_size)
        x_left_origin = x_min
        x_right_origin = x_min+self.grid_size
        y_top_origin = y_max
        y_bottom_origin = y_max-self.grid_size

        grid_geometries_list = []

        for i in range(x_ceil):

            y_top = y_top_origin
            y_bottom = y_bottom_origin

            for j in range(y_ceil):

                grid_geometries_list.append(((x_left_origin, y_top), (x_right_origin, y_top), (
                    x_right_origin, y_bottom), (x_left_origin, y_bottom)))
                y_top = y_top-self.grid_size
                y_bottom = y_bottom-self.grid_size

            x_left_origin = x_left_origin+self.grid_size
            x_right_origin = x_right_origin+self.grid_size

        if self.cut:

            if all(self.shapefile.eval("geometry.type == 'Polygon' or geometry.type == 'MultiPolygon'")):

                grid_geometries = gpd.GeoDataFrame(geometry=pd.Series(grid_geometries_list).apply(lambda x: Polygon(
                    x)), crs=self.shapefile.crs).intersection(unary_union(self.shapefile.geometry).convex_hull)

            else:

                grid_geometries = gpd.GeoDataFrame(geometry=pd.Series(grid_geometries_list).apply(lambda x: Polygon(
                    x)), crs=self.shapefile.crs).intersection(unary_union(self.shapefile.geometry).convex_hull)

            grid_geometries = grid_geometries[grid_geometries.geometry.type == 'Polygon']
            grid_geometries.index = [i for i in range(len(grid_geometries))]

            return gpd.GeoDataFrame(geometry=grid_geometries).reset_index(drop=True)

        else:

            return gpd.GeoDataFrame(index=[i for i in range(len(grid_geometries_list))], geometry=pd.Series(grid_geometries_list).apply(lambda x: Polygon(x)), crs=self.shapefile.crs).reset_index(drop=True)

    def outputs(self, shapefile, project_dirs):

        self.shapefile = shapefile[0]
        self.shapefile_datum = shapefile[1]
        self.project_dirs = project_dirs

        grid_geodataframe = self.create_grid(
            self.shapefile, self.grid_size_float_text.value, cut=True)
        figure, axes = plt.subplots(figsize=(15, 15))
        grid_geodataframe_overlay = get_ipython().run_line_magic(
            'time', "gpd.overlay(self.shapefile, grid_geodataframe, how='intersection')")
        grid_geodataframe_overlay = grid_geodataframe_overlay.explode(
        ).reset_index(level=1, drop=True)
        grid_geodataframe_centroids = grid_geodataframe_overlay.centroid
        self.shapefile.boundary.plot(ax=axes, color='black', linewidth=0.5)
        grid_geodataframe_overlay.plot(
            ax=axes, linewidth=0.5, color='white', zorder=2)
        grid_geodataframe_overlay.boundary.plot(
            ax=axes, linewidth=0.5, color='black', zorder=3)
        grid_geodataframe_size = self.grid_size_float_text.value
        grid_geodataframe_boundary = self.shapefile['geometry'].boundary
        grid_geodataframe_datum = self.shapefile_datum
        shapefile_geodataframe = self.shapefile
        axes.grid(color='lightgrey', linewidth=0.5, linestyle='-', alpha=0.5)
        axes_scalebar_font_properties = FontProperties(size=8)
        axes_scalebar = AnchoredSizeBar(axes.transData, 1000, '1.0 km', loc=3, pad=0.5, color='black',
                                        frameon=True, borderpad=0.5, sep=5, fontproperties=axes_scalebar_font_properties)
        axes.add_artist(axes_scalebar)
        axes.set_axisbelow(True)
        axes.margins(0.2, 0.2)
        axes_anchored_text = AnchoredText('Área: %.1f km²\nPerímetro: %.1f km\nMalha: %.1f m' % (
            (self.shapefile.area[0]/1000000), self.shapefile.length[0]/1000, self.grid_size_float_text.value), prop=dict(size=8), loc=2, borderpad=0.5, frameon=False)
        axes.add_artist(axes_anchored_text)

        grid_geodataframe_name = str(self.project_dirs['dir'][6]).lower().replace(' ', '_')+'_'+str(
            grid_geodataframe_datum.lower().replace(':', '_'))+'_' + str(self.grid_size_float_text.value).replace('.', '_')+'_m'
        grid_outputs_dirs = [os.path.join(self.project_dirs['dir'][4], grid_geodataframe_name, 'grid').replace(
            '\\', '/'), os.path.join(self.project_dirs['dir'][5], grid_geodataframe_name).replace('\\', '/')]

        for i in grid_outputs_dirs:

            try:

                os.makedirs(i)

            except OSError as Error:

                if os.path.exists(i):

                    pass

        grid_geodataframe_overlay.to_file(os.path.join(grid_outputs_dirs[1], str(
            grid_geodataframe_name)+'.shp'), encoding="utf-8", driver='ESRI Shapefile')
        plt.savefig(os.path.join(grid_outputs_dirs[0], str(
            grid_geodataframe_name)+'.png'), dpi=600, bbox_inches='tight')
        plt.show()

        print("Imagem salva em:\n%s\n" % (os.path.join(
            grid_outputs_dirs[0], str(grid_geodataframe_name)+'.png')).replace('\\', '/'))

        print("Malha processada salva em:\n%s\n" % (os.path.join(
            grid_outputs_dirs[1], str(grid_geodataframe_name)+'.shp')).replace('\\', '/'))

        return grid_geodataframe_boundary, grid_geodataframe_centroids.reset_index(drop=True), grid_geodataframe_size, grid_geodataframe_overlay.reset_index(drop=True), grid_geodataframe_datum, shapefile_geodataframe, grid_geodataframe_name


class WidgetsWindFetchs(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        wind_directions_list = ['0.0°', '22.5°', '45.0°', '67.5°', '90.0°', '112.5°', '135.0°',
                                '157.5°', '180.0°', '202.5°', '225.0°', '247.5°', '270.0°', '292.5°', '315.0°', '337.5°']
        self.wind_directions_select_multiple = widgets.SelectMultiple(
            description='Direções (°):', options=wind_directions_list, layout=Layout(width='30%'), style={'description_width': 'initial'})
        self.specific_wind_direction_text = widgets.Text(description='Direção (°):', value='', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.method_toggle_buttons = widgets.ToggleButtons(
            options=['Método SPM', 'Método de Saville'], button_style='')
        methods_accordion = widgets.Accordion(
            children=[self.method_toggle_buttons])
        methods_accordion.set_title(
            0, 'Escolha do método de cálculo de pistas de vento')
        wind_directions_accordion = widgets.Accordion(
            children=[self.wind_directions_select_multiple, self.specific_wind_direction_text])
        wind_directions_accordion.set_title(0, 'Direções convencionais')
        wind_directions_accordion.set_title(1, 'Direção específica')
        tab_contents = ['Métodos', 'Direções']
        tab_children = [methods_accordion, wind_directions_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        return tab

    def intersection(self, geometry, centroid, wind_direction):

        self.geometry_intersection = geometry
        self.centroid_intersection = centroid
        self.wind_direction_intersection = wind_direction

        x_min = self.geometry_intersection.bounds['minx'][0]
        y_min = self.geometry_intersection.bounds['miny'][0]
        x_max = self.geometry_intersection.bounds['maxx'][0]
        y_max = self.geometry_intersection.bounds['maxy'][0]
        line_length = (max(abs(x_min-x_max), abs(y_max-y_min)))*2
        line = LineString([self.centroid_intersection, [(self.centroid_intersection.x+(np.sin(np.deg2rad(self.wind_direction_intersection))
                                                                                       * line_length)), (self.centroid_intersection.y+(np.cos(np.deg2rad(self.wind_direction_intersection))*line_length))]])
        intersection = self.geometry_intersection.intersection(line)
        intersection = intersection[0]

        if intersection.geom_type == 'MultiPoint':

            iterator = chain(intersection)
            multipoint_distances_list = [
                self.centroid_intersection.distance(i) for i in iterator]

            return (intersection[multipoint_distances_list.index(min(multipoint_distances_list))])

        elif intersection.geom_type == 'Point':

            return intersection

        else:

            return None

    def saville(self, geometry, centroid, wind_direction):

        self.geometry_saville = geometry
        self.centroid_saville = centroid
        self.wind_direction_saville = wind_direction

        def radians(rad): return math.radians(rad)
        def cosines(cos): return math.cos(cos)
        radians_method = np.vectorize(radians)
        cosines_method = np.vectorize(cosines)
        linspace = scipy.linspace(
            self.wind_direction_saville+45, self.wind_direction_saville-45, 19)
        radians_linspace = scipy.linspace(45, -45, 19)
        radians_wind_directions = radians_method(radians_linspace)
        cosines_wind_directions = cosines_method(radians_wind_directions)
        iterator = chain(linspace)
        saville_intersections_list = [self.intersection(
            self.geometry_saville, self.centroid_saville, i) for i in iterator]

        if None in saville_intersections_list:

            print("Não foi possível calcular a pista de vento corretamente no ponto: %s.\n" %
                  self.centroid_saville)

        else:

            iterator = chain(saville_intersections_list)
            saville_distances_list = [
                self.centroid_saville.distance(i) for i in iterator]
            wind_directions_range = np.arange(0, 19)

            return (sum([saville_distances_list[i]*cosines_wind_directions[i] for i in wind_directions_range])/sum(cosines_wind_directions))

    def spm(self, geometry, centroid, wind_direction):

        self.geometry_spm = geometry
        self.centroid_spm = centroid
        self.wind_direction_spm = wind_direction

        linspace = scipy.linspace(
            self.wind_direction_spm+24, self.wind_direction_spm-24, 9)
        iterator = chain(linspace)
        spm_intersections_list = [self.intersection(
            self.geometry_spm, self.centroid_spm, i) for i in iterator]

        if None in spm_intersections_list:

            print("Não foi possível calcular a pista de vento corretamente no ponto: %s.\n" %
                  self.centroid_spm)

        else:

            iterator = chain(spm_intersections_list)
            spm_distances_list = [
                self.centroid_spm.distance(i) for i in iterator]

            return np.mean(spm_distances_list)

    def saville_wind_fetchs(self, geometry, grid_centroids, wind_direction):

        self.geometry_saville_wind_fetchs = geometry
        self.grid_centroids_saville_wind_fetchs = grid_centroids
        self.wind_direction_saville_wind_fetchs = wind_direction

        progress_bar = FloatProgress(min=0, max=1, description=(
            '%0.2f°:' % (self.wind_direction_saville_wind_fetchs)))

        display(progress_bar)

        wind_fetchs_list = np.empty(
            len(self.grid_centroids_saville_wind_fetchs))
        c = 0

        for i in chain(self.grid_centroids_saville_wind_fetchs):

            wind_fetchs_list[c] = self.saville(
                self.geometry_saville_wind_fetchs, i, self.wind_direction_saville_wind_fetchs)
            progress_bar.value += 1 / \
                len(self.grid_centroids_saville_wind_fetchs)
            c = c+1

        return wind_fetchs_list

    def spm_wind_fetchs(self, geometry, grid_centroids, wind_direction):

        self.geometry_spm_wind_fetchs = geometry
        self.grid_centroids_spm_wind_fetchs = grid_centroids
        self.wind_direction_spm_wind_fetchs = wind_direction

        progress_bar = FloatProgress(min=0, max=1, description=(
            '%0.2f°:' % (self.wind_direction_spm_wind_fetchs)))

        display(progress_bar)

        wind_fetchs_list = np.empty(len(self.grid_centroids_spm_wind_fetchs))
        c = 0

        for i in chain(self.grid_centroids_spm_wind_fetchs):

            wind_fetchs_list[c] = self.spm(
                self.geometry_spm_wind_fetchs, i, self.wind_direction_spm_wind_fetchs)
            progress_bar.value += 1/len(self.grid_centroids_spm_wind_fetchs)
            c = c+1

        return wind_fetchs_list

    def outputs(self, grid, project_dirs):

        self.grid = grid
        self.grid_boundary = grid[0]
        self.grid_centroids = grid[1]
        self.project_dirs = project_dirs

        for i in range(0, len(self.grid_centroids)):

            if self.grid[3]['geometry'][i].contains(self.grid_centroids[i]):

                self.grid_centroids[i] = self.grid_centroids[i]

            else:

                self.grid_centroids[i] = self.grid[3]['geometry'][i].representative_point(
                )

        x_centroids_list = [self.grid_centroids[i].x for i in range(
            0, len(self.grid_centroids))]
        y_centroids_list = [self.grid_centroids[i].y for i in range(
            0, len(self.grid_centroids))]

        wind_fetchs_outputs_dir = os.path.join(
            self.project_dirs['dir'][3], str(self.grid[6])).replace('\\', '/')

        try:

            os.makedirs(wind_fetchs_outputs_dir)

        except OSError as Error:

            if os.path.exists(wind_fetchs_outputs_dir):

                pass

        wind_directions_list = []

        if len(self.wind_directions_select_multiple.value) == 0 and self.specific_wind_direction_text.value == '':

            messagebox.showwarning("ondisapy", "Nenhuma direção selecionada.")

            return None

        else:

            print('\nProcessando pistas de vento...')

            if len(self.wind_directions_select_multiple.value) != 0 and self.specific_wind_direction_text.value == '':

                for i in range(len(self.wind_directions_select_multiple.value)):

                    wind_direction = re.findall(
                        r'\d+', str(self.wind_directions_select_multiple.value[i]))
                    wind_direction = wind_direction[0]+'.'+wind_direction[1]
                    wind_direction = float(wind_direction)
                    wind_directions_list.append(wind_direction)

            elif len(self.wind_directions_select_multiple.value) == 0 and self.specific_wind_direction_text.value != '':

                self.specific_wind_direction_text.value = self.specific_wind_direction_text.value.replace(
                    ",", ".")
                wind_directions_list.append(
                    float(self.specific_wind_direction_text.value))

            elif len(self.wind_directions_select_multiple.value) != 0 and self.specific_wind_direction_text.value != '':

                for i in range(len(self.wind_directions_select_multiple.value)):

                    wind_direction = re.findall(
                        r'\d+', str(self.wind_directions_select_multiple.value[i]))
                    wind_direction = wind_direction[0]+'.'+wind_direction[1]
                    wind_direction = float(wind_direction)
                    wind_directions_list.append(wind_direction)

                self.specific_wind_direction_text.value = self.specific_wind_direction_text.value.replace(
                    ",", ".")
                wind_directions_list.append(
                    float(self.specific_wind_direction_text.value))

            wind_directions_list = sorted(list(set(wind_directions_list)))

            if self.method_toggle_buttons.value == 'Método de Saville':

                for i in wind_directions_list:

                    saville_wind_fetchs = get_ipython().run_line_magic(
                        'time', 'self.saville_wind_fetchs(self.grid_boundary, self.grid_centroids, i)')
                    saville_wind_fetchs_dataframe = pd.DataFrame(
                        {'0': x_centroids_list, '1': y_centroids_list, '2': saville_wind_fetchs, '3': None, '4': None})
                    saville_wind_fetchs_dataframe.iloc[0, 3] = i
                    saville_wind_fetchs_dataframe.iloc[0, 4] = 'saville'
                    saville_wind_fetchs_dataframe.to_csv(os.path.join(wind_fetchs_outputs_dir, str(
                        self.grid[6])+'_saville_'+str(i).replace('.', '_')+'.csv').replace('\\', '/'), sep=';', header=False, encoding='utf-8')

                    print("\nPistas de vento salvas em:\n%s\n" % os.path.join(wind_fetchs_outputs_dir, str(
                        self.grid[6])+'_saville_'+str(i).replace('.', '_')+'.csv').replace('\\', '/'))

            elif self.method_toggle_buttons.value == 'Método SPM':

                for i in wind_directions_list:

                    spm_wind_fetchs = get_ipython().run_line_magic(
                        'time', 'self.spm_wind_fetchs(self.grid_boundary, self.grid_centroids, i)')
                    spm_wind_fetchs_dataframe = pd.DataFrame(
                        {'0': x_centroids_list, '1': y_centroids_list, '2': spm_wind_fetchs, '3': None, '4': None})
                    spm_wind_fetchs_dataframe.iloc[0, 3] = i
                    spm_wind_fetchs_dataframe.iloc[0, 4] = 'spm'
                    spm_wind_fetchs_dataframe.to_csv(os.path.join(wind_fetchs_outputs_dir, str(
                        self.grid[6])+'_spm_'+str(i).replace('.', '_')+'.csv').replace('\\', '/'), sep=';', header=False, encoding='utf-8')

                    print("\nPistas de vento salvas em:\n%s\n" % os.path.join(wind_fetchs_outputs_dir, str(
                        self.grid[6])+'_spm_'+str(i).replace('.', '_')+'.csv').replace('\\', '/'))


class WidgetsWindFetchsVisualization(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        cmap_list = ['viridis', 'plasma', 'inferno', 'magma', 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper', 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic', 'Pastel1', 'Pastel2',
                     'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c', 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv', 'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar', 'cmo.thermal', 'cmo.haline', 'cmo.solar', 'cmo.ice',  'cmo.gray', 'cmo.oxy', 'cmo.deep', 'cmo.dense',  'cmo.algae', 'cmo.matter', 'cmo.turbid', 'cmo.speed', 'cmo.amp', 'cmo.tempo', 'cmo.phase', 'cmo.balance', 'cmo.delta', 'cmo.curl']
        self.cmap_dropdown = widgets.Dropdown(description='Seleção:', options=sorted(
            cmap_list, key=str.lower), layout=Layout(width='30%'), style={'description_width': 'initial'}, value='cmo.delta')
        self.load_wind_fetchs_button = widgets.Button(description='Importar pistas de vento processada(s)',
                                                      tooltip='Importa pistas de vento processada(s)', layout=Layout(width='30%'), style={'description_width': 'initial'})
        self.load_wind_fetchs_button.on_click(
            self.load_wind_fetchs_button_click)
        self.bins_int_text = widgets.IntText(value=10, description='Intervalos:', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        wind_fetchs_accordion = widgets.Accordion(
            children=[self.load_wind_fetchs_button])
        wind_fetchs_accordion.set_title(
            0, 'Importação de pistas de vento processada(s)')
        cmap_accordion = widgets.Accordion(children=[self.cmap_dropdown])
        cmap_accordion.set_title(0, 'Escolha do esquema de cores desejado')
        bins_accordion = widgets.Accordion(children=[self.bins_int_text])
        bins_accordion.set_title(
            0, 'Escolha do número de intervalos desejados')
        tab_contents = ['Pistas de Vento', 'Esquema de Cores', 'Intervalos']
        tab_children = [wind_fetchs_accordion, cmap_accordion, bins_accordion]
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
            wind_fetchs_list = [j/1000 for j in wind_fetchs_list]
            wind_direction = wind_fetchs_dataframe.loc[0, [4]].tolist()[0]
            wind_fetchs_method = wind_fetchs_dataframe.loc[0, [5]].tolist()[0]
            figure, axes = plt.subplots(figsize=(15, 15))
            self.grid[3]['wind_fetchs_values'] = wind_fetchs_list
            self.grid[3].plot(column='wind_fetchs_values', cmap=self.cmap_dropdown.value, ax=axes, antialiased=True, snap=True, scheme='equal_interval', k=self.bins_int_text.value,
                              legend=True, legend_kwds={'loc': 'lower right', 'fontsize': 8, 'edgecolor': 'black', 'fancybox': False, 'title': 'Intervalos (km)', 'title_fontsize': '8'})
            self.grid[0].plot(ax=axes, color='black', linewidth=0.5)
            axes_scalebar_font_properties = FontProperties(size=8)
            axes_scalebar = AnchoredSizeBar(axes.transData, 1000, '1.0 km', loc=3, pad=0.5, frameon=True,
                                            color='black', borderpad=0.5, sep=5, fontproperties=axes_scalebar_font_properties)
            axes.add_artist(axes_scalebar)
            axes.set_axisbelow(True)
            axes.margins(0.2, 0.2)
            axes.grid(color='lightgrey', linewidth=0.5,
                      linestyle='-', alpha=0.5)
            windrose_axes = figure.add_axes(
                [0, 0, 0.07, 0.07], projection='windrose')
            windrose_var = [1]
            windrose_dataframe = pd.DataFrame(
                {'bearing': wind_direction, 'var': windrose_var})
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

            wind_fetchs_visualization_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], str(self.grid[6]), 'wind_fetchs').replace('\\', '/')

            try:

                os.makedirs(wind_fetchs_visualization_outputs_dir)

            except OSError as Error:

                if os.path.exists(wind_fetchs_visualization_outputs_dir):

                    pass

            plt.savefig(os.path.join(wind_fetchs_visualization_outputs_dir, str(self.grid[6])+'_'+str(wind_fetchs_method)+'_'+str(
                wind_direction).replace('.', '_')+'.png').replace('\\', '/'), dpi=600, bbox_inches='tight')
            plt.show()

            print("Imagem salva em:\n%s\n" % os.path.join(wind_fetchs_visualization_outputs_dir, str(
                self.grid[6])+'_'+str(wind_fetchs_method)+'_'+str(wind_direction).replace('.', '_')+'.png').replace('\\', '/'))
