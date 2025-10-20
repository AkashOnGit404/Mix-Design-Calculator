from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo, showerror, showwarning
import openpyxl
import os
import numpy as np
from PIL import Image, ImageTk
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def round_up(value, decimals):
    factor = 10 ** decimals
    return np.ceil(value * factor) / factor


def calculate():
    coarse_aggregate_type = coarse_type_combobox.get()
    slump = int(slump_entrybox.get())
    concrete_type = concrete_type_var.get()
    exposure_condition = exposure_combobox.get()
    cement_type = cement_type_combobox.get()
    maximum_nominal_size = maximum_nominal_size_combobox.get()
    flyash_content_percentage = flyash_scale.get()
    ggbs_content_percentage = ggbs_scale.get()
    silicafume_content_percentage = silicafume_scale.get()
    flyash_sg = float(flyash_sg_entry.get())
    ggbs_sg = float(ggbs_sg_entry.get())
    silicafume_sg = float(silicafume_sg_entry.get())
    sand_zone = sand_zone_combobox.get()
    pumping = pumping_var.get()
    cement_sg = float(cement_sg_entry.get())
    coarse_sg = float(coarse_sg_entry.get())
    fine_sg = float(fine_sg_entry.get())
    plasticizer_sg = float(plasticizer_sg_entry.get())
    plastizer_dosage = float(plasticizer_dosage_entry.get())
    fa_free_moisture = float(fa_total_moisture_entry.get())-float(fa_water_absorption_entry.get())
    ca_free_moisture = float(ca_total_moisture_entry.get())-float(ca_water_absorption_entry.get())
    
    
        
    #Target Compressive Strength

    grade = grade_combobox.get()
    if grade.startswith("M"):
        grade_value = int(grade[1:])
        
        list_X = [([10,15],5.0),([20,25],5.5),([30,35,40,45,50,55,60],6.5),([65,70,75,80,85,90,95,100],8.0)]     #Table 1 IS 10262:2019
        list_S = [([10,15],3.5),([20,25],4.0),([30,35,40,45,50,55,60],5.0),([65,70,75,80,85],6.0)]               #Table 2 IS 10262:2019
        
        for i in list_X:
            for j in i[0]:
                if grade_value == j:
                    fck_1 = grade_value + i[1]            #Clause 4.2 of IS 10262:2019
                    break
        for i in list_S:
            for j in i[0]:
                if grade_value == j:
                    fck_2 = grade_value + 1.65*i[1]
                    break     
        
        target_strength = round_up(max(fck_1, fck_2), 3)
        
        
        
        #Entrapped Air
        table_3_list = [(10,1.5),(20,1.0),(40,0.8)]
        
        if maximum_nominal_size:
            for i in table_3_list:
                if i[0]==int(maximum_nominal_size):
                    entrapped_air = i[1]
                    
                    break
                
        
            #water Cement Ratio
            excel_path = resource_path("tables.xlsx")
            workbook = openpyxl.load_workbook(excel_path)
            ws1 = workbook["curve"]
            ws2 = workbook["Plain concrete"]
            ws3 = workbook["Reinforced concrete"]
            ws4 = workbook["Water content"]
            ws6 = workbook["Table 5"] 
            if cement_type:
                if cement_type == "33 Grade OPC":
                    for i in range(2,17):
                        if ws1["A"+str(i)].value==grade_value:
                            water_cement_ratio = ws1["B"+str(i)].value
                            
                            break
                elif cement_type == "43 Grade OPC" or cement_type=="PPC" or cement_type=="PSC" or cement_type=="Others":
                    for i in range(2,17):
                        if ws1["A"+str(i)].value==grade_value:
                            water_cement_ratio = ws1["C"+str(i)].value
                            
                            break
                elif cement_type == "53 Grade OPC":
                    for i in range(2,17):
                        if ws1["A"+str(i)].value==grade_value:
                            water_cement_ratio = ws1["D"+str(i)].value
                            break
                if water_cement_ratio != None:       
                    if concrete_type:
                        if concrete_type=='PCC':
                            ws_1 = ws2
                        else:
                            ws_1 = ws3
                        maximum_wc_ratio = 0    
                        if exposure_condition:
                            list_exposure = [("Mild",2),("Moderate",3),("Severe",4),("Very severe",5),("Extreme",6)]
                            for i in list_exposure:
                                if exposure_condition==i[0]:
                                    if grade_value >= ws_1["D"+str(i[1])].value:
                                        maximum_wc_ratio = ws_1["C"+str(i[1])].value
                                        minimum_cement_content = ws_1["B"+str(i[1])].value
                                        if int(maximum_nominal_size_combobox.get()) == 10:
                                            minimum_cement_content = minimum_cement_content+40                                    
                                        if int(maximum_nominal_size_combobox.get()) == 40:
                                            minimum_cement_content = minimum_cement_content-30
                                        break
                            if maximum_wc_ratio != 0:
                                if water_cement_ratio<=maximum_wc_ratio:
                                    
                                    if coarse_aggregate_type:
                                        if slump:
                                            for i in range(2,5):
                                                if ws4["A"+str(i)].value == int(maximum_nominal_size):
                                                    water_content = ws4["B"+str(i)].value
                                                    for j in range(2,6):
                                                        if coarse_aggregate_type==ws4["C"+str(j)].value:
                                                            water_content -= ws4["D"+str(j)].value
                                                            break
                                                    if slump != 50:
                                                        water_content = (((slump-50)/25)*0.03+1)*186
                                                        
                                                    
                                                    cement_content=water_content/water_cement_ratio
                                                    
                                                    if plasticizer_var.get():
                                                        for k in range (5,31):
                                                            water_content_1 = water_content
                                                            water_content_1 = (1-0.01*k)*water_content_1
                                                            cement_content = water_content_1/water_cement_ratio
                                                            if cement_content>=minimum_cement_content and cement_content <=450:
                                                                water_content=water_content_1
                                                                water_reduction_plasticizer = k
                                                                break
                                                    if cement_content>450:
                                                        showwarning("High Slump","It is suggested to use plasticizer. Else lower the slump or upgrade the cement grade or downgrade the concrete grade.")
                                                    else:
                                                        
                                                        #Miscellaneous Cementitious Materials
                                                        flyash_content = 0
                                                        ggbs_content = 0
                                                        silicafume_content = 0
                                                        cementitious_content = cement_content
                                                        if flyash_content_percentage!=0 or ggbs_content_percentage!=0 or silicafume_content_percentage!=0:
                                                            
                                                            for i in range (10,20) :
                                                                cementitious_content = cement_content*(1+0.01*i)
                                                                if (water_content/cement_content)>maximum_wc_ratio:
                                                                    continue
                                                                else:
                                                                    flyash_content = cementitious_content*0.01*flyash_content_percentage
                                                                    ggbs_content = cementitious_content*0.01*ggbs_content_percentage    
                                                                    silicafume_content = cementitious_content*0.01*silicafume_content_percentage    
                                                                    cement_content_2 = cementitious_content-(flyash_content+ggbs_content+silicafume_content)
                                                                    if cement_content_2>=minimum_cement_content and cement_content_2<=450 :
                                                                        break
                                                            cement_content=cement_content_2
                                                            water_cement_ratio = water_content/cementitious_content
                                                            
                                                        #Coarse Aggregate Calculation
                                                        if sand_zone:
                                                            for i in range(2,6):
                                                                coarse_vol=0
                                                                if str(ws6["A"+str(i)].value) == str(maximum_nominal_size):
                                                                    for j in range(1,5):
                                                                        char = chr(65+j)
                                                                        if ws6[char+"1"].value == sand_zone:
                                                                            coarse_vol = ws6[char+str(i)].value
                                                                            break
                                                                if coarse_vol!=0:
                                                                    break     
                                                    
                                                            coarse_vol = coarse_vol-0.01*((water_cement_ratio-0.5)/0.05)
                                                            if pumping :
                                                                coarse_vol *= 0.9
                                                            fine_vol = 1-coarse_vol
                                                            
                                                            #Mix calculation per unit volume
                                                            entrapped_air_vol = entrapped_air/100
                                                            cement_vol = cement_content/(cement_sg*1000)
                                                            flyash_vol = flyash_content/(flyash_sg*1000) 
                                                            ggbs_vol = ggbs_content/(ggbs_sg*1000) 
                                                            silicafume_vol = silicafume_content/(silicafume_sg*1000) 
                                                            water_vol = water_content/(1*1000) 
                                                            plasticizer_vol = (plastizer_dosage*cementitious_content)/(plasticizer_sg*100000)
                                                            all_aggregate_vol = 1-(entrapped_air_vol+cement_vol+flyash_vol+ggbs_vol+silicafume_vol+water_vol+plasticizer_vol)
                                                            
                                                            
                                                            #Masses of materials
                                                            cement_mass = cement_content
                                                            ca_mass_ssd = all_aggregate_vol*coarse_vol*coarse_sg*1000
                                                            fa_mass_ssd = all_aggregate_vol*fine_vol*fine_sg*1000
                                                            water_mass = water_content
                                                            plasticizer_mass = plastizer_dosage*cementitious_content*0.01
                                                            flyash_mass = flyash_content
                                                            ggbs_mass = ggbs_content
                                                            silicafume_mass = silicafume_content
                                                            
                                                            ca_mass = ca_mass_ssd*(1+0.01*ca_free_moisture)
                                                            fa_mass = fa_mass_ssd*(1+0.01*fa_free_moisture)
                                                            surplus_water = (ca_mass-ca_mass_ssd) + (fa_mass-fa_mass_ssd)
                                                            water_mass = water_mass - surplus_water
                                                            
                                                            
                                                            
                                                            if (cement_mass and ca_mass and fa_mass and water_mass and water_cement_ratio):
                                                                frame.grid_remove()
                                                                output_frame = Frame(root)
                                                                output_frame.place(x=0, y=0, height=680, width=850)
                                                                
                                                                for widget in output_frame.winfo_children():
                                                                    widget.destroy()
                                                                
                                                                concrete_detail_labelframe = LabelFrame(output_frame, text = "Concrete Details")
                                                                concrete_detail_labelframe.place(x=5,y=5, height=150, width=270)
                                                                Label(concrete_detail_labelframe, text=f"Grade:  {grade_combobox.get()}", anchor = "w").grid(row=0, column=0, sticky = "w")
                                                                Label(concrete_detail_labelframe, text=f"Concrete Type:  {concrete_type_var.get()}", anchor = "w").grid(row=1,column=0, sticky="w")
                                                                Label(concrete_detail_labelframe, text=f"Slump:  {slump}mm", anchor = "w").grid(row=2,column=0, sticky="w")
                                                                Label(concrete_detail_labelframe, text=f"Exposure Condition:  {exposure_condition}", anchor = "w").grid(row=2,column=0, sticky="w")
                                                                Label(concrete_detail_labelframe, text=f"Pumping Required:  {'Yes' if pumping_var else 'No'}", anchor = "w").grid(row=3,column=0, sticky="w")
                                                                
                                                                cement_detail_labelframe = LabelFrame(output_frame, text="Cement Details")
                                                                cement_detail_labelframe.place(x=280,y=5, height=150, width=270)
                                                                Label(cement_detail_labelframe, text=f"Cement Type:  {cement_type}", anchor = "w").grid(row=0,column=0, sticky="w")
                                                                Label(cement_detail_labelframe, text=f"Specific Gravity:  {cement_sg}", anchor = "w").grid(row=1,column=0, sticky="w")
                                                                
                                                                ca_detail_labelframe = LabelFrame(output_frame,text="Coarse Aggregate Details")
                                                                ca_detail_labelframe.place(x=555,y=5, height=150, width=290)
                                                                Label(ca_detail_labelframe, text=f"Aggregate Type:  {coarse_type_combobox.get()}", anchor = "w").grid(row=0, column=0, sticky="w")
                                                                Label(ca_detail_labelframe, text=f"Maximum Nominal Size:  {maximum_nominal_size}mm", anchor = "w").grid(row=1, column=0, sticky="w")
                                                                Label(ca_detail_labelframe, text=f"Specific Gravity(SSD):  {coarse_sg}", anchor = "w").grid(row=2, column=0, sticky="w")
                                                                Label(ca_detail_labelframe, text=f"Water Absorption(%):  {ca_water_absorption_entry.get()}%", anchor = "w").grid(row=3, column=0, sticky="w")
                                                                Label(ca_detail_labelframe, text=f"Total Moisture Content(%):  {ca_total_moisture_entry.get()}%", anchor = "w").grid(row=4, column=0, sticky="w")
                                                                
                                                                fa_detail_labelframe = LabelFrame(output_frame, text="Fine Aggregate Details")
                                                                fa_detail_labelframe.place(x=5,y=160, height=250, width=270)
                                                                Label(fa_detail_labelframe, text=f"Sand Zone:  {sand_zone}", anchor = "w").grid(row=0,column=0, sticky="w")
                                                                Label(fa_detail_labelframe, text=f"Specific Gravity(SSD):  {fine_sg}", anchor = "w").grid(row=1,column=0, sticky="w")
                                                                Label(fa_detail_labelframe, text=f"Water Absorption(%):  {fa_water_absorption_entry.get()}%", anchor = "w").grid(row=2, column=0, sticky="w")
                                                                Label(fa_detail_labelframe, text=f"Total Moisture Content(%):  {fa_total_moisture_entry.get()}%", anchor = "w").grid(row=3, column=0, sticky="w")
                                                                
                                                                cementitious_material_detail_labelframe = LabelFrame(output_frame, text = "Admixture Details")
                                                                cementitious_material_detail_labelframe.place(x=280,y=160, height=250, width=565)
                                                                Label(cementitious_material_detail_labelframe, text=f"Fly Ash(%):  {flyash_content_percentage}%", anchor = "w").grid(row=0, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"Specific Gravity:  {flyash_sg}", anchor = "w").grid(row=1, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"", anchor = "w").grid(row=2, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"Ground Granulated Blast Furnance Slag(%):  {ggbs_content_percentage}%", anchor = "w").grid(row=3, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"Specific Gravity:  {ggbs_sg}", anchor = "w").grid(row=4, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"", anchor = "w").grid(row=5, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"Silica Fume(%):  {silicafume_content_percentage}%", anchor = "w").grid(row=6, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"Specific Gravity:  {silicafume_sg}", anchor = "w").grid(row=7, column=0, sticky="w")
                                                                Label(cementitious_material_detail_labelframe, text=f"", anchor = "w").grid(row=8, column=0, sticky="w")
                                                                if plasticizer_var:
                                                                    Label(cementitious_material_detail_labelframe, text=f"Plasticizer Dosage:  {plasticizer_dosage_entry.get()}% by mass of cementitious material", anchor = "w").grid(row=9, column=0, sticky="w")
                                                                    Label(cementitious_material_detail_labelframe, text=f"Specific Gravity:  {plasticizer_sg}", anchor = "w").grid(row=10, column=0, sticky="w")
                                                                
                                                                output_labelframe = LabelFrame(output_frame, text="Mix Proportion")
                                                                output_labelframe.place(x=5,y=415, height=210, width=840)
                                                                Label(output_labelframe, text=f"Cement:  {cement_mass:.1f} kg/m³", anchor = "w").grid(row=0,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Coarse Aggregate:  {ca_mass:.1f} kg/m³", anchor = "w").grid(row=1,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Fine Aggregate:  {fa_mass:.1f} kg/m³", anchor = "w").grid(row=2,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Water:  {water_mass:.1f} kg/m³", anchor = "w").grid(row=3,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Water-Cement Ratio:  {round_up(water_cement_ratio,3)} ", anchor = "w").grid(row=4,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Fly Ash:  {flyash_mass:.1f} kg/m³", anchor = "w").grid(row=5,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Ground Granulated Blast Furnance Slag:  {ggbs_mass:.1f} kg/m³", anchor = "w").grid(row=6,column=0, sticky="w")
                                                                Label(output_labelframe, text=f"Silica Fume:  {silicafume_mass:.1f} kg/m³", anchor = "w").grid(row=7,column=0, sticky="w")
                                                                if plasticizer_var.get():
                                                                    Label(output_labelframe, text=f"Plasticizer:  {plasticizer_mass:.2f} kg/m³", anchor = "w").grid(row=8,column=0, sticky="w")
                                                                
                                                                def back():
                                                                    output_frame.destroy()
                                                                    
                                                                                                                            
                                                                    frame.grid()
                                                                
                                                                
                                                                Button(output_frame, text="OK",cursor="hand2", command=back).place(x=5, y=640, height=25, width=840)
                                                                
                                                            
                                                                
                                                        else:
                                                            showwarning("Sand Zone", "Please select a sand zone.")   
                                    
                                        else:
                                            showwarning("Slump value","Please enter a slump value.")
                                    
                                    else:
                                        showwarning("Type Of Coarse Aggregate", "Please select a type of coarse aggregate.")
                                
                                else:
                                    showwarning("Error", "Water-cement ratio is more than the maximum permissible water-cement ratio. Change cement type or increase the concrete grade.")
                            else:
                                showwarning("Low Grade", "The selected grade of concrete doesn't satisfy the minimum grade requirements for the given exposure condition. Please increase the concrete grade.")    
                        else:
                            showwarning("Exposure Condition", "Please describe the exposure conditions.")
                            
                    else:
                        showwarning("Concrete Type", "Please select the type of concrete.")
                else:
                    showwarning("Low Grade Cement", "Select a higher grade cement.") 
            else:
                showwarning("Cement Type", "Please select the cement type.")     
          
        else:
            showwarning("Maximum Nominal Size Of Coarse Aggregate", "Please select maximum nominal size of coarse aggregate.")    
        
    else:
        showwarning("No Selection", "Please select a concrete grade.")
        
        
    
        

root = Tk()
root.title("Mix-Design Calculator")
root.geometry("850x680")
root.resizable(False, False)
frame = Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10)
# --- Menu Bar ---
about_menu = Menu(root)

def show_about():
    about_window = Toplevel(root)
    about_window.geometry("500x500")
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    about_width = 500
    about_height = 500

    pos_x = root_x + (root_width // 2) - (about_width // 2)
    pos_y = root_y + (root_height // 2) - (about_height // 2)

    about_window.geometry(f"{about_width}x{about_height}+{pos_x}+{pos_y}")
    about_window.resizable(False, False)
    about_frame = Frame(about_window)
    about_frame.place(x=0,y=0, width=500, height=500)
    photo = PhotoImage(file=resource_path("about.png"))

    photo_label=Label(about_frame, image=photo)
    photo_label.image = photo
    photo_label.place(x=0,y=0)
    
about_menu.add_command(label="About", command=show_about)
root.config(menu=about_menu)


#Conrete Info

concrete_labelframe = LabelFrame(frame, text = "Concrete")
concrete_labelframe.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

grade_label = Label(concrete_labelframe, text="Grade")
grade_label.grid(row=0, column=0)

grade_combobox = ttk.Combobox(concrete_labelframe, values = ['M10','M15','M20','M25','M30','M35','M40','M45','M50','M55','M60','M65','M70','M75','M80'], state="readonly")
grade_combobox.grid(row=1, column=0)

concrete_type_labelframe = LabelFrame(concrete_labelframe, text='Concrete Type')
concrete_type_labelframe.grid(row=0, column=1, rowspan=2)
concrete_type_var = StringVar()
concrete_type_list = [("Plain Cement Concrete", "PCC"), ("Reinforced Cement Concrete", "RCC")]
for i in concrete_type_list:
    concrete_type_radiobutton = Radiobutton(concrete_type_labelframe, text=i[0], value=i[1], justify='left', variable=concrete_type_var)
    concrete_type_radiobutton.select()
    if i[1] == "PCC":
        concrete_type_radiobutton.grid(row=0, column=0, sticky='w')
    if i[1] == "RCC":
        concrete_type_radiobutton.grid(row=1, column=0, sticky='w')
        
slump_label = Label(concrete_labelframe, text = 'Slump(mm)')
slump_label.grid(row=0, column=2)
slump_entrybox = Entry(concrete_labelframe)
slump_entrybox.insert(0,0)
slump_entrybox.grid(row=1, column=2)

exposure_label = Label(concrete_labelframe, text = "Exposure Condition")
exposure_label.grid(row=0, column=3)
exposure_combobox = ttk.Combobox(concrete_labelframe, value = ["Mild", "Moderate", "Severe", "Very severe", "Extreme"], state = "readonly")
exposure_combobox.grid(row=1, column=3)

pumping_var=BooleanVar()
pumping_checkbutton = Checkbutton(concrete_labelframe, text = "Pumping required", onvalue=True, offvalue=False, variable=pumping_var)
pumping_checkbutton.grid(row=1, column=4)

for widget in concrete_labelframe.winfo_children():
    widget.grid_configure(padx=5, pady=5)

#Cement Information
cement_labelframe = LabelFrame(frame, text = "Cement")
cement_labelframe.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

cement_type_label = Label(cement_labelframe, text="Cement Type")
cement_type_label.grid(row=0, column=0)

cement_type_combobox = ttk.Combobox(cement_labelframe, values = ["33 Grade OPC", "43 Grade OPC", "53 Grade OPC", "PPC", "PSC", "Others"], state="readonly")
cement_type_combobox.grid(row=1,column=0)

cement_sg_label = Label(cement_labelframe, text="Specific Gravity")
cement_sg_label.grid(row=0, column=1)
cement_sg_entry = Entry(cement_labelframe)
cement_sg_entry.insert(0, 3.15)
cement_sg_entry.grid(row=1, column=1)

for widget in cement_labelframe.winfo_children():
    widget.grid_configure(padx=5, pady=5)
    

#Fine Aggregate

fine_aggregate_labelframe = LabelFrame(frame, text="Fine Aggregate")
fine_aggregate_labelframe.grid(row=2,column=0,sticky='nsew',padx=10, pady=5)

sand_zone_label = Label(fine_aggregate_labelframe, text="Sand Zone")
sand_zone_label.grid(row=0, column=0)
sand_zone_combobox = ttk.Combobox(fine_aggregate_labelframe, values = ["I", "II", "III", "IV"], state="readonly")
sand_zone_combobox.grid(row=1, column=0)

fine_sg_label = Label(fine_aggregate_labelframe, text ="Specific Gravity(SSD)")
fine_sg_label.grid(row=0, column=1)
fine_sg_entry = Entry(fine_aggregate_labelframe)
fine_sg_entry.insert(0, 2.65)
fine_sg_entry.grid(row=1, column=1)

fa_water_absorption_label = Label(fine_aggregate_labelframe, text="Water Absorption(%)")
fa_water_absorption_label.grid(row=0, column=3)
fa_water_absorption_entry = Entry(fine_aggregate_labelframe)
fa_water_absorption_entry.insert(0,0.0)
fa_water_absorption_entry.grid(row=1, column=3)

fa_total_moisture_label = Label(fine_aggregate_labelframe, text="Total Moisture Content(%)")
fa_total_moisture_label.grid(row=0, column=4)
fa_total_moisture_entry = Entry(fine_aggregate_labelframe)
fa_total_moisture_entry.insert(0, 0.0)
fa_total_moisture_entry.grid(row=1, column=4)


for widget in fine_aggregate_labelframe.winfo_children():
    widget.grid_configure(padx=5, pady=5)


#Coarse Aggregate 

coarse_aggregate_labelframe = LabelFrame(frame, text="Coarse Aggregate")
coarse_aggregate_labelframe.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

coarse_type_label = Label(coarse_aggregate_labelframe, text="Coarse Aggregate Type")
coarse_type_label.grid(row=0, column=0)
coarse_type_combobox = ttk.Combobox(coarse_aggregate_labelframe, values = ["Angular(Crushed)", "Sub-Angular", "Rounded", "Gravel(w/ Crushed)"], state="readonly")
coarse_type_combobox.grid(row=1, column=0)

maximum_nominal_size_label = Label(coarse_aggregate_labelframe, text="Maximum Nominal Size(mm)")
maximum_nominal_size_label.grid(row=0, column=1)
maximum_nominal_size_combobox = ttk.Combobox(coarse_aggregate_labelframe, values = [10,20,40], state="readonly")
maximum_nominal_size_combobox.grid(row=1, column=1)

coarse_sg_label = Label(coarse_aggregate_labelframe, text ="Specific Gravity(SSD)")
coarse_sg_label.grid(row=0, column=2)
coarse_sg_entry = Entry(coarse_aggregate_labelframe)
coarse_sg_entry.insert(0, 2.74)
coarse_sg_entry.grid(row=1, column=2)

ca_water_absorption_label = Label(coarse_aggregate_labelframe, text="Water Absorption(%)")
ca_water_absorption_label.grid(row=0, column=3)
ca_water_absorption_entry = Entry(coarse_aggregate_labelframe)
ca_water_absorption_entry.insert(0,0.0)
ca_water_absorption_entry.grid(row=1, column=3)

ca_total_moisture_label = Label(coarse_aggregate_labelframe, text="Total Moisture Content(%)")
ca_total_moisture_label.grid(row=0, column=4)
ca_total_moisture_entry = Entry(coarse_aggregate_labelframe)
ca_total_moisture_entry.insert(0, 0.0)
ca_total_moisture_entry.grid(row=1, column=4)

for widget in coarse_aggregate_labelframe.winfo_children():
    widget.grid_configure(padx=5, pady=5)


#Cementitious Material

cementitious_material_labelframe = LabelFrame(frame, text = "Cementitious Material")
cementitious_material_labelframe.grid(row=4, column=0, sticky='nsew', padx=10, pady=5)

flyash_labelframe = LabelFrame(cementitious_material_labelframe, text = "Fly Ash")
flyash_labelframe.grid(row=0, column=0, padx=5, pady=5)

flyash_content_label = Label(flyash_labelframe, text="Fly Ash Content(%)")
flyash_content_label.grid(row=0, column=0)
flyash_scale = Scale(flyash_labelframe, from_=0, to=30, orient="horizontal")
flyash_scale.grid(row=1, column=0)
flyash_sg_label = Label(flyash_labelframe, text="Specific Gravity")
flyash_sg_label.grid(row=0, column=1, pady=5)
flyash_sg_entry = Entry(flyash_labelframe)
flyash_sg_entry.grid(row=1, column=1)
flyash_sg_entry.insert(0,2.2)

ggbs_labelframe = LabelFrame(cementitious_material_labelframe, text = "GGBS")
ggbs_labelframe.grid(row=0, column=2, padx=20, pady=5,)

ggbs_content_label = Label(ggbs_labelframe, text="GGBS Content(%)")
ggbs_content_label.grid(row=0, column=0)
ggbs_scale = Scale(ggbs_labelframe, from_=0, to=50, orient="horizontal")
ggbs_scale.grid(row=1, column=0)
ggbs_sg_label = Label(ggbs_labelframe, text="Specific Gravity")
ggbs_sg_label.grid(row=0, column=1, pady=5)
ggbs_sg_entry = Entry(ggbs_labelframe)
ggbs_sg_entry.grid(row=1, column=1)
ggbs_sg_entry.insert(0,2.9)

silicafume_labelframe = LabelFrame(cementitious_material_labelframe, text = "Silica Fume")
silicafume_labelframe.grid(row=0, column=4, padx=5, pady=5)

silicafume_content_label = Label(silicafume_labelframe, text="Silica Fume Content(%)")
silicafume_content_label.grid(row=0, column=0)
silicafume_scale = Scale(silicafume_labelframe, from_=0, to=10, orient="horizontal")
silicafume_scale.grid(row=1, column=0)
silicafume_sg_label = Label(silicafume_labelframe, text="Specific Gravity")
silicafume_sg_label.grid(row=0, column=1, pady=5)
silicafume_sg_entry = Entry(silicafume_labelframe)
silicafume_sg_entry.grid(row=1, column=1)
silicafume_sg_entry.insert(0,2.2)


#Admixture

def plasticizer():
    if plasticizer_var.get():
        plasticizer_dosage_label.grid(row=0, column=1, padx=100)
        plasticizer_dosage_entry.grid(row=1, column=1, pady=5)
        
        plasticizer_sg_label.grid(row=0, column=2)
        plasticizer_sg_entry.grid(row=1, column=2, pady=5)
        
    else:
        plasticizer_dosage_label.grid_remove()
        plasticizer_dosage_entry.grid_remove()
        
        plasticizer_sg_label.grid_remove()
        plasticizer_sg_entry.grid_remove()
        
        
plasticizer_labelframe = LabelFrame(frame, text="Plasticizer")
plasticizer_labelframe.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)

plasticizer_var = BooleanVar()
plasticizer_checkbutton = Checkbutton(plasticizer_labelframe, text="Water Reducing Admixture", variable= plasticizer_var, onvalue=True, offvalue=False, command=plasticizer)
plasticizer_checkbutton.deselect()
plasticizer_checkbutton.grid(row=0, column=0)

plasticizer_dosage_label = Label(plasticizer_labelframe, text="Dosage(% of cementitious material)")
plasticizer_dosage_entry = Entry(plasticizer_labelframe)
plasticizer_dosage_entry.insert(0,1.0)

plasticizer_sg_label = Label(plasticizer_labelframe, text="Specific Gravity")
plasticizer_sg_entry = Entry(plasticizer_labelframe)
plasticizer_sg_entry.insert(0, 1.2)



#Calculate Button
calculate_button = Button(frame, text="Calculate", cursor="hand2", relief="raised", command=calculate)
calculate_button.grid(row=6, column=0, sticky='nsew', padx=10, pady=5)


root.mainloop()
        
        
#pyinstaller --onefile --windowed main.py --add-data "tables.xlsx;." --add-data "about.png;." 
        
        
        




