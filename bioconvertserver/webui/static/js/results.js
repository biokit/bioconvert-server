$(document).ready(function(){
    if (getStatus()==2){
        $("#computing").show();
        $.ajax({
            type: 'POST',
            url:'/api/BAM/BAM/',
            data:  {'identifier':getIdentifier()},
            success: function (data, textStatus, xhr) {
                console.log(data);
                $("#computing").hide();
                if(data["status"] == 5){
                    $("#error").show();
                    $("#error .text-danger").text(data["error_message"]);
                }else{
                    $("#done").show();
                }
            },
            error: function (textStatus, xhr) {
                console.error(textStatus.responseJSON);
                console.error(data);
            },
        });
    }else if (getStatus()==4){
        $("#computing").hide();
        $("#done").show();
        $("#error").hide();
    }else if (getStatus()==5){
        $("#computing").hide();
        $("#error").show();
        $("#done").hide();
    }
});