//run by using nodemon --inspect index.js
const Discord = require('discord.js');
const { Client, Attachment } = require('discord.js');
const client = new Discord.Client();
const Jimp = require('jimp');
const tesseract = require('node-tesseract-ocr');
let request = require(`request`);
let fs = require(`fs`);
const week = 1;
client.on('ready', () => {
 console.log(`Logged in as ${client.user.tag}!`);
 });

async function myCrop(inPath, outPath){
	const img = await Jimp.read(inPath);
	img.crop(240,160,275,460).write(outPath);
}
async function myfunc(path,dateTime){
	const img = await Jimp.read(path);
	var height = img.bitmap.height;
	var width = img.bitmap.width;
	//Now convert image to dark text on white background
	//1. Greyscale
	img.color([{apply:'greyscale', params: [50]}]);
	//2. Invert
	img.invert();
	var recolorPath = 'Results/Complete/'+dateTime+'_recolor.png';	
	img.write(recolorPath);
	setTimeout(function() {afterTimeout2(dateTime,recolorPath);}, 3000);
	/*
	var x;
	var y;
	var rHigh = 260;
	var rLow = 150;
	var gHigh = 135;
	var gLow = 125;
	var bHigh = 85;
	var bLow = 70;
	for (x = 0; x < width/2; x++) { 
		for (y = 0; y < height/2; y++) {
			var numSame = 0;
			var hex = await img.getPixelColor(x,y);
			var {r,g,b,a} = await Jimp.intToRGBA(hex);
			if(r >= rLow && r <= rHigh){
				numSame++;
			}
			if(g >= gLow && g <= gHigh){
				numSame++;
			}
			if(b >= bLow && b <= bHigh){
				numSame++;
			}
			if(numSame > 2){
				console.log('X:'+x+' Y:'+y+' is R:'+r+' G:'+g+' B:'+b+'\n\n');
				return;
			}
		}
	}
	console.log('no valid pixel found\n\n');
	*/
}
async function afterTimeout1(dateTime,path,cropPath){
	console.log('timeout complete');
	/*
			recolor club tags in image
				-get height and width
				-loop through all pixels
					-use image.getPixelColor(x,y) to get hex of pixel
					-convert hex using Jimp.intToRGBA(hex)
					-if club tag RGB, then recolor to black
				-save image
	*/
	const img = await Jimp.read(cropPath);
	var height = img.bitmap.height;
	var width = img.bitmap.width;
	//console.log(height+' - '+width);
	var x;
	var y;
	var blackHex = Jimp.rgbaToInt(0,0,0,255);
	/*
	console.log('hex = '+hex);
	console.log('blackHex = '+blackHex);
	console.log('vals = '+r+' - '+g+' - '+b+' - '+a);
	*/
	for (x = 0; x < width; x++) { 
		for (y = 0; y < height; y++) { 
			var hex = await img.getPixelColor(x,y);
			var {r,g,b,a} = await Jimp.intToRGBA(hex);
			if((b>=25 && b<=130)){
				img.setPixelColor(blackHex,x,y);
			}
		}
	}
	
	//Now convert image to dark text on white background
	//1. Greyscale
	img.color([{apply:'greyscale', params: [50]}]);
	//2. Invert
	img.invert();
	var recolorPath = 'Results/Complete/'+dateTime+'_recolor.png';	
	img.write(recolorPath);
	console.log('timeout starting');
	setTimeout(function() {afterTimeout2(dateTime,recolorPath);}, 3000);
}
async function afterTimeout2(dateTime,recolorPath){
	/*
		pass image into ocr and process text
		
	*/
	const config = {
		lang: 'eng',
		oem: 1,
		psm: 3
	}
 
	tesseract.recognize(recolorPath, config).then(text => {
		console.log('Result:\n', text)
	}).catch(err => {
		console.log('error:', err)
	});
	
	
	/*
		query google docs for usernames found
		place results into correct location
	*/
}
client.on('message', msg => {
 if (msg.channel.id === '617414947214721024') {
	
	if(msg.attachments.first()){
		//msg.channel.send('attachment present');
		console.log('new image\n');
		var today = new Date();
		var date = today.getFullYear()+'_'+(today.getMonth()+1)+'_'+today.getDate();
		var time = today.getHours() + "_" + today.getMinutes() + "_" + today.getSeconds();
		var dateTime = date+'_'+time;
		var path = 'Results/'+dateTime+'.png';
		var cropPath = 'Results/'+dateTime+'_cropped.png';
		var dest = fs.createWriteStream(path);
		request.get(msg.attachments.first().url)
        .on('error', console.error)
        .pipe(dest);
		
		/*
		dest.on('close',() => {myCrop(path, cropPath)});
		console.log('timeout starting');
		setTimeout(function() {afterTimeout1(dateTime,path,cropPath);}, 3000);
		*/
		dest.on('close',() => {myfunc(path,dateTime)});
	}
 }
 
 });


client.login('NjE3MzkzMTI3NzQwOTMyMDk2.XWqfDw.MACVI9k0bAa_eTmjTPpyUHAztok');