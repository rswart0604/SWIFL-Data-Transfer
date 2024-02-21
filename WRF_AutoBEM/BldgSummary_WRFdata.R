library(dplyr)
library(stringr)
library(tidyr)
#library(ff)
#library(ffbase)
library(R.utils)

#check memory limit and then allocate more memory to R!
memory.limit()
memory.limit(size=56000)

#Read in data source of WRF output in csv format.  The csv will contain every coordinate, and every value at every time step for that coordinate.  THe result is usually too large to view in Excel so often the only way to access the data in this format is to bring it into R.
#ORNL Campus
data=read.csv("R://WRFOutputCSV/90mResults/epvars90m_orbldg_2015.maincampus.csv", header=FALSE)
#Chicago Morph1 
#- this file is 3GB and R struggles to read it the usual way with read.csv but with allocating more memory it helps!
chi0=read.csv("R://WRFOutputCSV/90mResults/epvars90m_ChiLoopOnly_2015.Loop.csv", header=FALSE)
chi1=read.csv("R://WRFOutputCSV/90mResults/epvars90m_ChiMorph1_2015.Loop.csv", header=FALSE)
chi2=read.csv("R://WRFOutputCSV/90mResults/epvars90m_ChiMorph2_2015.Loop.csv", header=FALSE)
#use the ff package instead
#chi1.ff=read.csv.ffdf(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph1_2015.Loop.csv", header=FALSE)
#Chicago Morph2
#chi2=read.csv("C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph2_2015.Loop.csv", header=FALSE)
#chi2.ff=read.csv.ffdf(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph1_2015.Loop.csv", header=FALSE)
#ABOVE read it in but had it's own issues when trying to continue from there

#can read in the file by splitting it in half? This worked but never finished it as I switched to increasing memory to NOT have to split the data.
# countLines("C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph1_2015.Loop.csv")
# 16954080/2
# chi1.1=read.csv(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph1_2015.Loop.csv", header=FALSE, nrows=8477040)
# chi1.2=read.csv(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph1_2015.Loop.csv", header=FALSE, skip=8477040)
# 
# countLines("C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph2_2015.Loop.csv")
# 16719120/2
# chi2.1=read.csv(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph2_2015.Loop.csv", header=FALSE, nrows=8359560)
# chi2.2=read.csv(file="C:/Users/6q9/Desktop/melissa_climate/chicago/epvars90m_ChiMorph2_2015.Loop.csv", header=FALSE, skip=8359560)


#Can view information about the data file by using the command: summary(data) or str(data)
#library(psych) has a nice set of tools for summary statistics

#The coordinates are in two separate columns.  FOr our purposes I join the coordinates into one column with the values separated by a space.
data$coord=paste(data$V3,data$V4,sep=" ")
chi0$coord=paste(chi0$V3,chi1$V4,sep=" ")
chi1$coord=paste(chi1$V3,chi1$V4,sep=" ")
chi2$coord=paste(chi2$V3,chi2$V4,sep=" ")

# chi1.1$coord=with(chi1.1,paste(chi1.1$V3,chi1.1$V4,sep=" "))
# chi1.2$coord=with(chi1.2,paste(chi1.2$V3,chi1.2$V4,sep=" "))
# chi2.1$coord=with(chi2.1,paste(chi2.1$V3,chi2.1$V4,sep=" "))
# chi2.2$coord=with(chi2.2,paste(chi2.2$V3,chi2.2$V4,sep=" "))

#wrote the chi files to csv at this point in the script so if need to can import them from here without going through the skipping of rows

#names are specifichi_c order to this particular file
names(data)=c("OID","Time_UTC","Lat","Lon","Temp.K.","DewPoint.K.","RelHumid","Pressure","RadDir.Wm.2.","RadDiff.Wm.2.","LWRad","SWNorm","SWRad","WindDir.from.","WindSpeed.ms.1.","SnowDepth.cm.","RainDepth.mm.","x","coord")
cnames=c("OID","Time_UTC","Lat","Lon","Temp.K.","DewPoint.K.","RelHumid","Pressure","RadDir.Wm.2.","RadDiff.Wm.2.","LWRad","SWNorm","SWRad","WindDir.from.","WindSpeed.ms.1.","SnowDepth.cm.","x","coord")
names(chi1)=cnames
names(chi2)=cnames
names(chi0)=cnames

# names(chi1.1)=cnames
# names(chi1.2)=cnames
# names(chi2.1)=cnames
# names(chi2.2)=cnames

#add columns with temperature and precipication converted to US units
data$T_F=data$Temp.K.*(9/5)-459.67
data$Rain_in=data$RainDepth.mm./25.4
chi0$T_F=chi0$Temp.K.*(9/5)-459.67 # todo
chi1$T_F=chi1$Temp.K.*(9/5)-459.67
chi2$T_F=chi2$Temp.K.*(9/5)-459.67

#output 1 timestep to import grid into arcgis
#only need to pull one grid for Chicago
t=subset(chi2, chi2$Time_UTC=="2015-01-01_00:00:00")
write.csv(t, "R:/bldgs_ORNL_Chicago/Chicago/grid_bldg2coord_90m/chi_90m_grid.csv")

k=subset(data, data$Time_UTC=="2015-01-02_20:00:00" )
write.csv(k, "R:/bldgs_ORNL_Chicago/ORNL/grid_bldg2coord_90m/ORNL_90m_grid.csv")
#add in buildings and coordinates as determined through GIS
#read in file of building ID and coordinate in following format example: 35.930916 -84.316711;35.930916 -84.315674
bcoord=read.csv("R:/bldgs_ORNL_Chicago/ORNL/grid_bldg2coord_90m/ORNL_90m_wrfcoord2bldg.csv", header=TRUE)

c0coord=read.csv("R://bldgs_ORNL_Chicago/Chicago/grid_bldg2coord_90m/chi0_90m_wrfcoord2bldg.csv", header=TRUE)
c1coord=read.csv("R://bldgs_ORNL_Chicago/Chicago/grid_bldg2coord_90m/chi1_90m_wrfcoord2bldg.csv", header=TRUE)
c2coord=read.csv("R://bldgs_ORNL_Chicago/Chicago/grid_bldg2coord_90m/chi2_90m_wrfcoord2bldg.csv", header=TRUE)

#if needed format coordinate column so the precision of the values matches in both coord and data data sets 

#keep only bldg id and coord #todo coord is of the form "41.867863 -87.628662"
bc=bcoord[,c(4,24)]
c0=c0coord[,c(5,27)]
c1=c1coord[,c(5,27)]
c2=c2coord[,c(5,27)]


#format coordinate as character and replace ";" with ","
bc$coord=gsub(";",",",bc$coord)
c0$coord=gsub(";",",",c0$coord)
c1$coord=gsub(";",",",c1$coord)
c2$coord=gsub(";",",",c2$coord)


#Run the below for ORNL to summarize data for each building into separate dataframes
#not including all parameters; tailor as needed

#to just write to individual dataframes
for (i in bc$BLDG)
  assign(paste("b",i,sep=""),subset(data,coord %in% unlist(strsplit(subset(bc,BLDG==i)$coord,","))) %>%
           group_by(Time_UTC)%>%
           summarise(T_K=mean(Temp.K.),
                     T_F=mean(T_F),
                     RH=mean(RelHumid),
                     DewPoint_K=mean(DewPoint.K.),
                     Pressure=mean(Pressure),
                     RadDir_Wm2=mean(RadDir.Wm.2.),
                     RadDiff_Wm2=mean(RadDiff.Wm.2.),
                     LWRad=mean(LWRad),
                     SWNorm=mean(SWNorm),
                     SWRad=mean(SWRad),
                     WindDir_from=mean(WindDir.from.),
                     WindSpd_ms=mean(WindSpeed.ms.1.)))

#and to do the above but also write output to csv:
for (i in bc$BLDG)
  write.table(subset(data,coord %in% unlist(strsplit(subset(bc,BLDG==i)$coord,","))) %>%
                group_by(Time_UTC)%>%
                summarise(T_K=mean(Temp.K.),
                          T_F=mean(T_F),
                          RH=mean(RelHumid),
                          DewPoint_K=mean(DewPoint.K.),
                          Pressure=mean(Pressure),
                          RadDir_Wm2=mean(RadDir.Wm.2.),
                          RadDiff_Wm2=mean(RadDiff.Wm.2.),
                          LWRad=mean(LWRad),
                          SWNorm=mean(SWNorm),
                          SWRad=mean(SWRad),
                          WindDir_from=mean(WindDir.from.),
                          WindSpd_ms=mean(WindSpeed.ms.1.)),
              file=paste("//GUARNERI/Urban-MET/bldgs_ORNL_Chicago/ORNL/Bldg_weather_90m/ORNL",i,".csv",sep=""),row.names = FALSE, sep=",",quote=FALSE)


# chi bldg wrf summary ----------------------------------------------------

#Run the below to summarize data for each building into separate dataframes


#write output to csv:
for (i in c0$BLDGID)
  write.table(subset(chi0,coord %in% unlist(strsplit(subset(c0,BLDGID==i)$coord,","))) %>%
                group_by(Time_UTC)%>%
                summarise(T_K=mean(Temp.K.),
                          T_F=mean(T_F),
                          RH=mean(RelHumid),
                          DewPoint_K=mean(DewPoint.K.),
                          Pressure=mean(Pressure),
                          RadDir_Wm2=mean(RadDir.Wm.2.),
                          RadDiff_Wm2=mean(RadDiff.Wm.2.),
                          LWRad=mean(LWRad),
                          SWNorm=mean(SWNorm),
                          SWRad=mean(SWRad),
                          WindDir_from=mean(WindDir.from.),
                          WindSpd_ms=mean(WindSpeed.ms.1.)),
              file=paste("//GUARNERI/Urban-MET/bldgs_ORNL_Chicago/Chicago/CHIbldg_weather_90m/NoMorph/Chi0_BldgWeather_90m_",i,".csv",sep=""),row.names = FALSE, sep=",",quote=FALSE)

for (i in c1$BLDGID)
  write.table(subset(chi1,coord %in% unlist(strsplit(subset(c1,BLDGID==i)$coord,","))) %>%
                group_by(Time_UTC)%>%
                summarise(T_K=mean(Temp.K.),
                          T_F=mean(T_F),
                          RH=mean(RelHumid),
                          DewPoint_K=mean(DewPoint.K.),
                          Pressure=mean(Pressure),
                          RadDir_Wm2=mean(RadDir.Wm.2.),
                          RadDiff_Wm2=mean(RadDiff.Wm.2.),
                          LWRad=mean(LWRad),
                          SWNorm=mean(SWNorm),
                          SWRad=mean(SWRad),
                          WindDir_from=mean(WindDir.from.),
                          WindSpd_ms=mean(WindSpeed.ms.1.)),
              file=paste("//GUARNERI/Urban-MET/bldgs_ORNL_Chicago/Chicago/CHIbldg_weather_90m/Morph1/Chi1_BldgWeather_90m_",i,".csv",sep=""),row.names = FALSE, sep=",",quote=FALSE)


for (i in c2$BLDGID)
  write.table(subset(chi2,coord %in% unlist(strsplit(subset(c2,BLDGID==i)$coord,","))) %>%
                group_by(Time_UTC)%>%
                summarise(T_K=mean(Temp.K.),
                          T_F=mean(T_F),
                          RH=mean(RelHumid),
                          DewPoint_K=mean(DewPoint.K.),
                          Pressure=mean(Pressure),
                          RadDir_Wm2=mean(RadDir.Wm.2.),
                          RadDiff_Wm2=mean(RadDiff.Wm.2.),
                          LWRad=mean(LWRad),
                          SWNorm=mean(SWNorm),
                          SWRad=mean(SWRad),
                          WindDir_from=mean(WindDir.from.),
                          WindSpd_ms=mean(WindSpeed.ms.1.)),
              file=paste("//GUARNERI/Urban-MET/bldgs_ORNL_Chicago/Chicago/CHIbldg_weather_90m/Morph2/Chi2_BldgWeather_90m_",i,".csv",sep=""),row.names = FALSE, sep=",",quote=FALSE)

