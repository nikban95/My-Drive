function loadNotificationCount(){
  $.ajax('/get/notificationcount/' + Math.random(), method='GET')
  .then(
      function success(json_obj) {
        if(json_obj.count>0){
          $('#notification-count').html(json_obj.count);
        }
      }
  );
}

function loadNotification(){
  var notification = $('#notification'),
    notificationBox = $('#notificationBox');

  $.ajax({
    type: 'GET',
    url: '/get/notification/' + Math.random(),
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      notificationBox.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data){
    notificationBox.find('.overlay').remove();
    $('#notification-count').text('');
    notification.html(data);
  }).fail(function(data){
    notificationBox.find('.overlay').remove();
    $.notify(
      "Notification Loading Failed.",
      {
        position: "top center",
        className: 'error',  
      });
  });
}

function loadActivity(){
  var activity = $('#activity'),
    activityBox = $('#activityBox');

  $.ajax({
    type: 'GET',
    url: '/get/activity/' + Math.random(),
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      activityBox.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data){
    activityBox.find('.overlay').remove();
    activity.html(data);
  }).fail(function(data){
    activityBox.find('.overlay').remove();
    $.notify(
      "Activity Loading Failed.",
      {
        position: "top center",
        className: 'error',  
      });
  });
}

loadNotificationCount()
// update notification count
var myVar = setInterval(loadNotificationCount, 30000);

// load notification on button click
$('#notification-button').click(function() {
  loadNotification();
});

// load activity on button click
$('#activity-button').click(function() {
  loadActivity();
});

// username suggestions in share form
$('#id_username').tokenfield({
  autocomplete: {
    source: "/get/username/",
    delay: 100,
  },
  createTokensOnBlur: true,
})

// radio button
$('.rowfile').click(function() {
  var file_radio=$(this).find('input[name="obj"]');
  if(file_radio.is(':checked')){
    file_radio.prop("checked", false);
    $('.btn-group').hide();
    // $(this).attr("style", "background-color: #fff;");
    $(this).removeClass("info");
  }
  else{
    file_radio.prop("checked", true);
    $('.btn-group').hide();
    permission = $(this).find('#permission')[0].innerText;
    if(permission == "Owner"){
      $('#owner-btn-group').show();
      $('#write-btn-group').show();
      $('#read-btn-group').show();
    }
    else if(permission == "Write"){
      $('#write-btn-group').show();
      $('#read-btn-group').show();
    }
    else if(permission == "Read"){
      $('#read-btn-group').show();
    }
    // $(this).attr("style", "background-color: #f0f0f0;").siblings().attr("style", "background-color: #fff;");
    $(this).addClass("info").siblings().removeClass("info");
  }          
});

// clear in the search bar at main page
document.getElementById("clear-btn").onclick = function fun() {
  document.getElementById("id_filename").value="";
}

// create folder form submit ajax
$("#newfolderForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this),
      name = $form.find('input[name="foldername"]').val(),
      token = $form.find('input[name="csrfmiddlewaretoken"]').val(),
      url = $form.attr('action'),
      modalContent = $('#newfolder .box');

  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      foldername: name,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();
    $('#newfolder').modal('hide');
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else if(data.success){
      $.notify(
      data.success,
      {
        position: "top center",
        className: 'success',  
      });
      history.go(0);
    }
    $form.find('input[name="foldername"]').val("");
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    modalContent.find('.overlay').remove();
    $('#newfolder').modal('hide');
    $.notify(
      "Request Failed.",
      {
        position: "top center",
        className: 'error',  
      });
    $form.find('input[name="foldername"]').val("");
  });
});

// rename form submit ajax
$("#renameForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this);
      newname = $form.find('input[name="newname"]').val(),
      obj = $('body').find('input[name="obj"]:checked').val(),
      token = $form.find('input[name="csrfmiddlewaretoken"]').val(),
      url = $form.attr('action'),
      modalContent = $('#rename .box');

  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      newname: newname,
      obj: obj,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();
    $('#rename').modal('hide');
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      $.notify(
      data.success,
      {
        position: "top center",
        className: 'success',  
      });
      history.go(0);
    }
    $form.find('input[name="newname"]').val("");
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    modalContent.find('.overlay').remove();
    $('#rename').modal('hide');
    $.notify(
      "Request Failed.",
      {
        position: "top center",
        className: 'error',  
      });
    $form.find('input[name="newname"]').val("");
  });
});

// change description form submit ajax
$("#chngDescForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this);
      newdesc = $form.find('textarea[name="newdesc"]').val(),
      obj = $('body').find('input[name="obj"]:checked').val(),
      token = $form.find('input[name="csrfmiddlewaretoken"]').val(),
      url = $form.attr('action'),
      modalContent = $('#chngDesc .box');

  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      newdesc: newdesc,
      obj: obj,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();
    $('#chngDesc').modal('hide');
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      $.notify(
      data.success,
      {
        position: "top center",
        className: 'success',  
      });
      history.go(0);
    }
    $form.find('textarea[name="newdesc"]').val("");
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    modalContent.find('.overlay').remove();
    $('#chngDesc').modal('hide');
    $.notify(
      'Request Failed.',
      {
        position: "top center",
        className: 'error',  
      }
    );
    $form.find('textarea[name="newdesc"]').val("");
  });
});

// send the delete request
// onclick on delete button function
function sendDeleteRequest(){
  if(confirm('Are you sure you want to delete this file/folder?')){
    var obj = $('body').find('input[name="obj"]:checked').val(),
        token = $('body').find('input[name="csrfmiddlewaretoken"]').val(),
        url = "/delete/";

    // Send the data using post
    $.post(url, {
        obj: obj,
        csrfmiddlewaretoken: token,
    }).done(function(data) {
      // success or errors in post request
      if(data.error){
        $.notify(data.error,
        {
          position: "top center",
          className: 'error',  
        });
      }
      else{
        $.notify(
        data.success,
        {
          position: "top center",
          className: 'success',  
        });
        history.go(0);
      }
    }).fail(function(jqXHR, textStatus, errorThrown){
      // server failures etc.
      $.notify(
        "Request Failed.",
        {
          position: "top center",
          className: 'error',  
        }
      );
    });
  }
}

// send the delete forever request
// onclick on delete forever button function
function sendDeleteForeverRequest(){
  if(confirm('Are you sure you want to delete this file/folder permanently?')){
    var obj = $('body').find('input[name="obj"]:checked').val(),
        token = $('body').find('input[name="csrfmiddlewaretoken"]').val(),
        url = "/delete-forever/";

    // Send the data using post
    $.post(url, {
        obj: obj,
        csrfmiddlewaretoken: token,
    }).done(function(data) {
      // success or errors in post request
      if(data.error){
        $.notify(data.error,
        {
          position: "top center",
          className: 'error',  
        });
      }
      else{
        $.notify(
        data.success,
        {
          position: "top center",
          className: 'success',  
        });
        history.go(0);
      }
    }).fail(function(jqXHR, textStatus, errorThrown){
      // server failures etc.
      $.notify(
        "Request Failed.",
        {
          position: "top center",
          className: 'error',  
        }
      );
    });  
  }
}

// send the restore button request
// onclick on restore button function
function sendRestoreRequest(){
  var obj = $('body').find('input[name="obj"]:checked').val(),
      token = $('body').find('input[name="csrfmiddlewaretoken"]').val(),
      url = "/restore-delete/";

  // Send the data using post
  $.post(url, {
      obj: obj,
      csrfmiddlewaretoken: token,
  }).done(function(data) {
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      $.notify(
      data.success,
      {
        position: "top center",
        className: 'success',  
      });
      history.go(0);
    }
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    $.notify(
      "Request Failed.",
      {
        position: "top center",
        className: 'error',  
      }
    );
  });  
}

// share form submit ajax
$("#shareForm").submit(function(event) {
  event.preventDefault();

  var $form = $(this);
      usernames = $form.find('input[name="username"]').val(),
      access = $form.find('input[name="access"]:checked').val(),
      obj = $('body').find('input[name="obj"]:checked').val(),
      token = $form.find('input[name="csrfmiddlewaretoken"]').val(),
      url = $form.attr('action'),
      modalContent = $('#share .box');

  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      usernames: usernames,
      access: access,
      obj: obj,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();
    $('#share').modal('hide');
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      for(user in data.successUsers){
        $.notify(
          "Successfully shared with " + data.successUsers[user],
          {
          position: "top center",
          className: 'success',  
        });
      }
      for(user in data.failUsers){
        $.notify(
          "Sharing failed for " + data.failUsers[user],
          {
          position: "top center",
          className: 'error',  
        });
      }
    }
    $form.find('input[name="username"]').val("");
    $form.find('div[class="token"]').remove();
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    modalContent.find('.overlay').remove();
    $('#share').modal('hide');
    $.notify(
      "Request Failed.",
      {
        position: "top center",
        className: 'error',  
      }
    );
    $form.find('input[name="username"]').val("");
    $form.find('div[class="token"]').remove();
  });
});

// load manageVersions modal content
$('#manageVersions-button').click(function() {
  var body = $('body'),
      obj = body.find('input[name="obj"]:checked').val(),
      token = body.find('input[name="csrfmiddlewaretoken"]').val(),
      manageVersionsBody = $('#manageVersions .modal-body'),
      url = '/manage-versions/',
      modalContent = $('#manageVersions .box');
  
  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      obj: obj,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      manageVersionsBody.html("");
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();
    // success or errors in post request
    if(data.error){
      $('#manageVersions').modal('hide');
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      manageVersionsBody.html(data);
    }
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    modalContent.find('.overlay').remove();
    $('#manageVersions').modal('hide');
    $.notify(
      "Error Loading Manage Versions Content",
      {
        position: "top center",
        className: 'error',  
      });
  });
});

// send the restore version button request
// onclick on restore version button function
function sendRestoreVersionRequest(){
  var versionId= $('body').find('input[name="versionId"]').val(),
      token = $('body').find('input[name="csrfmiddlewaretoken"]').val(),
      url = "/version-restore/";

  // Send the data using post
  $.post(url, {
      versionId: versionId,
      csrfmiddlewaretoken: token,
  }).done(function(data) {
    // success or errors in post request
    if(data.error){
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      $.notify(
      data.success,
      {
        position: "top center",
        className: 'success',  
      });
      $('#manageVersions').modal('hide');
    }
  }).fail(function(jqXHR, textStatus, errorThrown){
    // server failures etc.
    $.notify(
      "Request Failed.",
      {
        position: "top center",
        className: 'error',  
      }
    );
  });  
}

// load viewPermissions modal content
$('#viewPermissions-button').click(function() {
  var body = $('body'),
      obj = body.find('input[name="obj"]:checked').val(),
      token = body.find('input[name="csrfmiddlewaretoken"]').val(),
      viewPermissionsBody = $('#viewPermissions .modal-body'),
      url = '/view-permissions/',
      modalContent = $('#viewPermissions .box');
  
  // Send the data using post
  $.ajax({
    type: 'POST',
    url: url,
    data: {
      obj: obj,
      csrfmiddlewaretoken: token,
    },
    beforeSend: function(jqXHR, settings){
      // display the loading icon
      viewPermissionsBody.html("");
      modalContent.append('<div class="overlay"><i class="fa fa-refresh fa-spin"></i></div>');
    }
  }).done(function(data) {
    modalContent.find('.overlay').remove();    
    // success or errors in post request
    if(data.error){
      $('#viewPermissions').modal('hide');
      $.notify(data.error,
      {
        position: "top center",
        className: 'error',  
      });
    }
    else{
      viewPermissionsBody.html(data);
    }
  }).fail(function(jqXHR, textStatus, errorThrown){
    modalContent.find('.overlay').remove();
    $('#viewPermissions').modal('hide');
    // server failures etc.
    $.notify(
      "Error Loading View Permissions Content",
      {
        position: "top center",
        className: 'error',  
      });
  });
});