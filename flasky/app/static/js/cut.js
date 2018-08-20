//1、拖拽显示图片
var handler={
	init:function($container){
		//需要把dargover的默认行为禁掉，不然会跳页
		$container.on("dragover",function(event){
			event.preventDefault();
		});
		$container.on("drop",function(event){
			event.preventDefault();
			//这里获取拖过来的图片文件，为一个File对象
			varfile=event.originalEvent.DataTransfer.files[0];  //获取文件图片，然后传给下一行处理
			handler.handleDrop($(this),file);
		})
	}
}

//如果使用input，则监听input的change事件：
//$container.on("change","input[type=file]",function(event){
//	if(!this.value)return;
//	varfile=this.files[0];                                     //获取File对象，同样传给handleDrop进行处理
//	handler.handleDrop($(this).closet(".container"),file);     //读取file的内容，并把它转成base64的格式
//	this.value="";
//});

handleDrop:function($container,file){
	var$img=$container.find("img");
	handler.readImgFile(file,$img,$container);
}
//在readImgFile里面读取图片文件内容，使用FileReader读取文件

readImgFile:function(file,$img,$container){
	var reader=new FileReader(file);
	//检验用户是否选择是图片文件
	if(file.type.split("/")[0]!=="image"){
		util.toast("You should choose an image file");
		return;
	}
	reader.onload=function(event){
		varbase64=event.target.result;
		handler.compressAndUpload($img,base64,file,$container);
	}
	reader.readAsDataURL(file);
}
//通过FileReader读取文件内容，调的是readAsDataURL,这个API能够把二进制图片内容转成base64的格式，读取玩之后会触发onload事件，在onload里面进行显示和上传。


//获取图片base64内容
varbase64=event.target.result;
//如果图片大于1MB,将body置半透明
if(file.size>ONE_MB){
	$("body").css("opacity",0.5);
}
$img.attr("src",baseUrl);
//还原
if(file.size>ONE_MB){
	$("body").css("opacity",1);
}
//调用一个压缩和上传的函数
handler.compressAndUpload($img,file,$container);
