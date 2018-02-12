import glob 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cbook as cbook
data_paths = glob.glob('/home/hayley/bounds_ay250_homework/hw_2/hw_2_data/*')
data_paths
fig_dat = pd.read_csv(data_paths[3])
fig_dat = fig_dat.dropna()

fig, ax1 = plt.subplots()





annot = ax1.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)


datas = []
poses= []
cols = []
for year in fig_dat.year.unique():
	for typer in fig_dat.type.unique():
		data = fig_dat.gpw[(fig_dat.year == year) & (fig_dat.type == typer)].values
		datas.append(data)
		poses.append(year)
		if typer == 'NVIDIA GPU':
			cols.append('b')
		else:
			cols.append('g')

boxes = plt.boxplot(datas, positions = poses, patch_artist = True)

for patch, color in zip(boxes['boxes'], cols):
        patch.set_facecolor(color)
for patch in boxes['boxes']:
	patch.set_alpha(.1)

temp = fig_dat[fig_dat.type == 'NVIDIA GPU']
temp2 = fig_dat[fig_dat.type == 'supercomputer'].sample(100)
temp = temp.append(temp2)
fig_dat = temp
fig_dat = fig_dat.append(pd.DataFrame([[2016,'IBM True North', 457.11]], columns=['year','type','gpw']))
fig_dat = fig_dat.append(pd.DataFrame([[2016,'Tensor Processing Unit', 100]], columns=['year','type','gpw']))
fig_dat.loc[fig_dat.type == 'NVIDIA GPU','color'] = 'b'
fig_dat.loc[fig_dat.type == 'supercomputer','color'] = 'g'
fig_dat.loc[fig_dat.type == 'IBM True North','color'] = 'y'
fig_dat.loc[fig_dat.type == 'Tensor Processing Unit','color'] = 'm'
sc = plt.scatter(fig_dat.year, fig_dat.gpw, c=fig_dat.color)
ax1.set_yscale('log')

names = np.asarray(fig_dat.type)
names = ['NGPU' if n == 'NVIDIA GPU' else n for n in names]
names = ['SP' if n == 'supercomputer' else n for n in names]
names = [n + ' ' + str(i) for i, n in enumerate(names)]

def update_annot(ind):
    pos = sc.get_offsets()[ind["ind"][0]]
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = "\n".join([names[n] for n in ind["ind"]])
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)



def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax1:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

print(ax1.get_figure())
ax1.get_figure().canvas.mpl_connect("motion_notify_event", hover)
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
plt.show()
