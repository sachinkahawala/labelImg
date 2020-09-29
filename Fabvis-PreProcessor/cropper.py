import cv2
import os
import PIL.Image
import numpy as np

# Set theseeeee

sourcefolderpath="../sample/slub"

targetfolderpath="target"

slideHeight = 256
slideWidth = 256
jump = 36

def checkContain(x1,y1,x2,y2,defect):
	dx,dy=defect[1],defect[2]
	dleftX,dleftY=dx-defect[3]/2,dy-defect[4]/2
	#### using defect center contains in frame
	# if(x1<=dx<=x2 and y1<=dy<=y2):
	# 	return 1
	### using rectangle overlap
	newX1 = max(x1,dleftX)
	newX2 = min(x2,dleftX+defect[3])
	newY1 = max(y1,dleftY)
	newY2 = min(y2,dleftY+defect[4])
	if(newX1<newX2 and newY1<newY2):
		return 1
	return 0

def getBoxCoordinates(x1,y1,x2,y2,defect):
	#### using defect center contains in frame
	# boxW = min(x2,defect[1]+defect[3]/2)-max(x1,defect[1]-defect[3]/2)
	# boxH = min(y2,defect[2]+defect[4]/2)-max(y1,defect[2]-defect[4]/2)
	# boxX,boxY = defect[1]-x1,defect[2]-y1
	# return [defect[0],boxX/slideWidth,boxY/slideHeight,boxW/slideWidth,boxH/slideHeight]

	### using rectangle overlap
	dx,dy=defect[1],defect[2]
	dleftX,dleftY=dx-defect[3]/2,dy-defect[4]/2
	newX1 = max(x1,dleftX)
	newX2 = min(x2,dleftX+defect[3])
	newY1 = max(y1,dleftY)
	newY2 = min(y2,dleftY+defect[4])

	boxW = newX2-newX1
	boxH = newY2-newY1
	boxX,boxY = newX1+boxW/2-x1,newY1+boxH/2-y1
	##return [defect[0],boxX,boxY,boxW,boxH]
	return [defect[0],boxX/slideWidth,boxY/slideHeight,boxW/slideWidth,boxH/slideHeight]

def cropper(imageWithPath, slideHeight, slideWidth, jump):
	image =  imageWithPath[0]
	imageName = imageWithPath[1].split('.')[0]
	imageH, imageW, channels = image.shape
	imageArray = []
	print( image.shape)
	defects=[]
	with open(sourcefolderpath+"/"+imageName+".txt", 'r') as fd:
		for line in fd:
			ty,dx,dy,dw,dh=map(float,line.split())
			ty=int(ty)
			dx,dy,dw,dh=round(dx*imageW),round(dy*imageH),round(dw*imageW),round(dh*imageH)
			defects.append([ty,dx,dy,dw,dh])
			#print(defects[-1])

	noOfFullH = int((imageH-slideHeight)/jump)
	noOfFullW = int((imageH-slideWidth)/jump)
	dCount,ndCount=0,0
	for i in range(0, noOfFullH+1):
		for j in range(0, noOfFullW+1):
			cropped = image[i*jump:(i*jump)+slideHeight, j*jump:(j*jump)+slideWidth]
			imageArray.append([cropped,[j*jump,i*jump,(j*jump)+slideWidth,(i*jump)+slideHeight]])
		if (imageW>((noOfFullW*jump)+slideWidth)):
			cropped = image[i*jump:(i*jump)+slideHeight, imageW-slideWidth:imageW]
			imageArray.append([cropped,[imageW-slideWidth,i*jump,imageW,(i*jump)+slideHeight]])

	if (imageH>((noOfFullH*jump)+slideHeight)):
		for j in range(0, noOfFullW+1):
			cropped = image[imageH-slideHeight:imageH, j*jump:(j*jump)+slideWidth]
			imageArray.append([cropped,[j*jump,imageH-slideHeight,(j*jump)+slideWidth,imageH]])

		if (imageW>(noOfFullW*slideWidth)):
			cropped = image[imageH-slideHeight:imageH, imageW-slideWidth:imageW]
			imageArray.append([cropped,[imageW-slideWidth,imageH-slideHeight,imageW,imageH]])
	for croppedImage in imageArray:
		x1,y1,x2,y2=croppedImage[1]
		flag = True
		defectCoorInCropped=[]
		for defect in defects:
			if(checkContain(x1,y1,x2,y2,defect)):
				defectCoorInCropped.append(" ".join(map(str,getBoxCoordinates(x1,y1,x2,y2,defect))))
				flag = False
		if not flag:
			nameImage = sourcefolderpath+"/"+imageName+"_Diffective_"+str(dCount)+".bmp"
			nameYolo = sourcefolderpath+"/"+imageName+"_Diffective_"+str(dCount)+".txt"
			bmpSave(nameImage,croppedImage[0])
			with open(nameYolo, 'w') as out_file:
				for newDefect in defectCoorInCropped:
						out_file.write(newDefect+"\n")
			dCount +=1		
		else:
			nameImage = sourcefolderpath+"/"+imageName+"_NonDiffective_"+str(ndCount)+".bmp"
			bmpSave(nameImage,croppedImage[0])
			ndCount+=1
	return imageArray
# def calculateRelativeDistance():

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append([img, str(filename)])
    return images

def bmpSave(filename, image):
	imagetemp = PIL.Image.fromarray(image.astype(np.uint8))
	imagetemp.save(filename)
	if imagetemp.mode != 'RGB':
		imagetemp=imagetemp.convert('RGB')

imageslist = load_images_from_folder(sourcefolderpath)
#print(imageslist)
for each in imageslist:
    
    croppedArrayOfOneImage = cropper(each, slideHeight, slideWidth, jump)
#     count = 0

#     for eachImage in croppedArrayOfOneImage:
#         imageName = targetfolderpath + '/' + each[1][:-4] +  '_' + str(count) + '.bmp'
#         count += 1
#         cv2.imwrite(imageName, eachImage)
#         print(imageName)