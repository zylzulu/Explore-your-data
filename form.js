$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				dbb : $('#db').val(),
				kww : $('#keywords').val()
			},
			type : 'POST',
			url : '/process',
			dataType:'json',
			error: function(){alert("NO DATA!! PLEASE TRY OTHER WORDS ^-^");
			window.location.reload();}
		})
		.done(function(result) {
		if (JSON.stringify(result) === '{}') {
		alert("NO DATA!! PLEASE TRY OTHER WORDS ^-^");
		window.location.reload();
		}
		var world_key=["Code","ID","CountryCode","language"];
		var emails_key=["Id","PersonId","EmailId","EId","AId","ERId","SenderPersonId"];
		var empleyee_key=["dep_no","dept_no","emp_no"];
		var tableindex=0;
		var db_key=[]
		if($('#db').val()=="hillary-clinton-emails"){db_key=emails_key;}
		if($('#db').val()=="employee"){db_key=empleyee_key;}
		if($('#db').val()=="world"){db_key=world_key;}
		for(let[key,val] of Object.entries(result)){
		var str= key+" table:<br><br>";
	    var tab = $('<table class="table table-border" align = "center" border="1"/>');
	    if(tableindex==0){$('#result').html(str);}
		else{$('#result').append(str);}
		// add headers
		var columns = [];
		var header = $('<tr/>');
		for(var i=0;i<val.length;i++){
		    var row = val[i];
		for(let[attr,value] of Object.entries(val[i])){
		if ($.inArray(attr, columns) == -1) {
						columns.push(attr);
						// Creating the header
						header.append($('<th/>').html(attr));
					}
		}
		}
		tab.append(header);
		// add data
		for(var i=0;i<val.length;i++){
		    var row = $('<tr/>');
		for(var j=0;j<columns.length;j++){
                if($.inArray(columns[j], Object.keys(val[i])) == -1){
                var content="";
                var td=$("<td/>").attr("id",key+','+columns[j]+','+content).html(content);
                }
                else{
                for(let[att,valu] of Object.entries(val[i])){
                if(columns[j]==att){
                if(db_key.indexOf(att) > -1){
                content="<a href='' onclick='return navi(this);'>"+valu+"</a>";
                var td=$("<td/>").attr("id",key+','+columns[j]+','+valu).html(content);
                }
                else{content=valu;
                var td=$("<td />").attr("id",key+','+columns[j]+','+content).html(content);
                }
                }
                }
                }
		    row.append(td);
		    }
		tab.append(row)
		}
			    $('#result').append(tab);
			    tableindex++;

		}
	}

	);
		event.preventDefault();

});
});
