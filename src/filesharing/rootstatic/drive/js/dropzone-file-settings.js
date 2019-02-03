// "myDropzone" is the camelized version of the HTML element's ID
Dropzone.options.uploadDropzone = {
    paramName: "fileDb",   //the dictionary name of the file for post
    autoProcessQueue: true,    //auto upload file
    previewsContainer: "#upload-dropzone",  //id my-dropzone div is dropdown region
    uploadMultiple: false,  //donot upload multiple files simultaneously
    addRemoveLinks: true,   //add remove links under thumbnail
    dictCancelUpload: "Cancel",
    dictRemoveFile: "Remove",
    maxFilesize: 10,        //in mb

    init: function () {

        this.on('sending', function (data, xhr, formData) {
            formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value);
        });

        this.on('success', function(file, response){
            // notification for successful upload
            $.notify(
              response.success,
              {
                position: "top center",
                className: 'success',  
              }
            );
        });
    }
};

$('#uploadFile').on('hide.bs.modal', function(e){
    history.go(0);
})

Dropzone.options.updateDropzone = {
    paramName: "fileDb",   //the dictionary name of the file for post
    autoProcessQueue: true,    //auto upload file
    previewsContainer: "#update-dropzone",  //id my-dropzone div is dropdown region
    uploadMultiple: false,  //donot upload multiple files simultaneously
    maxFiles: 1,    //maximum files that can be uploaded
    addRemoveLinks: true,   //add remove links under thumbnail
    dictCancelUpload: "Cancel",
    dictRemoveFile: "Remove",
    maxFilesize: 10,        //in mb

    init: function () {

        this.on('sending', function (data, xhr, formData) {
            obj = obj = $('body').find('input[name="obj"]:checked').val();
            formData.append("csrfmiddlewaretoken",document.getElementsByName("csrfmiddlewaretoken")[0].value);
            formData.append("obj", obj);
        });

        this.on('success', function(file, response){
            // notification for successful upload
            $.notify(
              response.success,
              {
                position: "top center",
                className: 'success',  
              }
            );
            this.removeFile(file);
            $('#updateFile').modal('hide');
        });
    }
};