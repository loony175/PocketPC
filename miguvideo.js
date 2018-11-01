var page=require('webpage').create();
var url=require('system').args[1];

page.onResourceRequested=function(requestData,networkRequest){
    if(/^https?:\/\/.*\.png.*$/.test(requestData.url)){
        networkRequest.abort();
    }
    if(/^https?:\/\/tv\.miguvideo\.com\/api\/new-vcms\/content\/getcontent\?.*$/.test(requestData.url)){
        content=requestData.url;
    }
    if(/^https?:\/\/tv\.miguvideo\.com\/apph\/newrlive\/rlive\/getUrl_h\?.*$/.test(requestData.url)){
        url_h=requestData.url;
        headers=requestData.headers;
    }
    if(content&&url_h&&headers){
        var row={};
        row.content=content;
        row.url_h=url_h;
        row.headers=headers;
        console.log(JSON.stringify(row));
        phantom.exit();
    }
}
page.open(url);
