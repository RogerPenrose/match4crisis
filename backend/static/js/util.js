function upadateLinksElementParams(a_tag,params){
    const splitted_href = a_tag.href.split("?");
    const route = splitted_href[0];
    const rest = splitted_href[1] ? splitted_href[1] : "";

    for (i = 0; i < params.length; i++){
        if (rest.indexOf(params[i][0] + "=") >= 0)
        {
            var prefix = rest.substring(0, rest.indexOf(params[i][0] + "=")); 
            var suffix = rest.substring(rest.indexOf(params[i][0] + "="));
            suffix = suffix.substring(suffix.indexOf("=") + 1);
            suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
            rest = prefix + params[i][0] + "=" + params[i][1] + suffix;
        }
        else
        {
            rest += "&" + params[i][0] + "=" + params[i][1];
        }
    }
    
    a_tag.href = `${ route }?${ rest }`
}