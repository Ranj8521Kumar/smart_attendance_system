import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ImageUploadPage extends StatefulWidget {
  final String subjectCode;
  final String subjectName;

  const ImageUploadPage({
    Key? key,
    required this.subjectCode,
    required this.subjectName,
  }) : super(key: key);

  @override
  _ImageUploadPageState createState() => _ImageUploadPageState();
}

class _ImageUploadPageState extends State<ImageUploadPage> {
  List<File> _selectedImages = [];
  List<double> _uploadProgress = [];
  bool _isUploading = false;

  void _showPickerOptions() {
    showModalBottomSheet(
      context: context,
      builder: (_) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: Icon(Icons.camera_alt),
              title: Text('Take Photo'),
              onTap: () {
                _pickImageFromCamera();
                Navigator.of(context).pop();
              },
            ),
            ListTile(
              leading: Icon(Icons.photo_library),
              title: Text('Choose from Device'),
              onTap: () {
                _pickImagesFromGallery();
                Navigator.of(context).pop();
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImageFromCamera() async {
    final picker = ImagePicker();
    final pickedImage = await picker.pickImage(source: ImageSource.camera);

    if (pickedImage != null) {
      setState(() {
        _selectedImages.add(File(pickedImage.path));
        _uploadProgress.add(0.0);
      });
    }
  }

  Future<void> _pickImagesFromGallery() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: true,
    );

    if (result != null && result.files.isNotEmpty) {
      setState(() {
        for (var file in result.files) {
          _selectedImages.add(File(file.path!));
          _uploadProgress.add(0.0);
        }
      });
    }
  }

  Future<void> _uploadImagesToServer() async {
    final serverUrl = dotenv.env['SERVER_URL'] ?? '';
    setState(() {
      _isUploading = true;
    });

    final uri = Uri.parse('$serverUrl/upload_images');

    for (int i = 0; i < _selectedImages.length; i++) {
      var request = http.MultipartRequest('POST', uri);
      request.fields['subjectCode'] = widget.subjectCode;
      request.fields['subjectName'] = widget.subjectName;

      try {
        var imageFile = await http.MultipartFile.fromPath('images[]', _selectedImages[i].path);
        request.files.add(imageFile);

        var streamedResponse = await request.send();

        streamedResponse.stream.listen(
              (value) {
            setState(() {
              _uploadProgress[i] += streamedResponse.contentLength != null
                  ? value.length / streamedResponse.contentLength!
                  : 0.0;
            });
          },
          onDone: () async {
            if (streamedResponse.statusCode == 200) {
              setState(() {
                _uploadProgress[i] = 1.0;
              });
              if (i == _selectedImages.length - 1) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Images uploaded successfully!')),
                );
                setState(() {
                  _selectedImages.clear();
                  _uploadProgress.clear();
                  _isUploading = false;
                });
              }
            } else {
              final responseBody = await streamedResponse.stream.bytesToString();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Upload failed for image ${i + 1}.')),
              );
              setState(() {
                _isUploading = false;
              });
            }
          },
          onError: (e) {
            print("Error uploading image ${i + 1}: $e");
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Error uploading image ${i + 1}.')),
            );
            setState(() {
              _isUploading = false;
            });
          },
        );
      } catch (e) {
        print("Error with image ${i + 1}: $e");
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error uploading image ${i + 1}.')),
        );
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  void _previewImage(File imageFile) {
    showDialog(
      context: context,
      builder: (_) => Dialog(
        child: InteractiveViewer(
          child: Image.file(imageFile),
        ),
      ),
    );
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImages.removeAt(index);
      _uploadProgress.removeAt(index);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // No AppBar here
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Column(
          children: [
            const SizedBox(height: 20),
            const SizedBox(height: 200),
            Center(
              child: GestureDetector(
                onTap: _showPickerOptions,
                child: Column(
                  children: [
                    Icon(Icons.cloud_upload_outlined, size: 100, color: Colors.blueAccent),
                    const SizedBox(height: 8),
                    Text(
                      "Upload classroom images",
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.blueGrey,
                        fontWeight: FontWeight.w500,
                      ),
                    )
                  ],
                ),
              ),
            ),
            const SizedBox(height: 30),
            if (_selectedImages.isNotEmpty)
              Expanded(
                child: GridView.builder(
                  padding: const EdgeInsets.all(10),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                  ),
                  itemCount: _selectedImages.length,
                  itemBuilder: (ctx, i) => Stack(
                    children: [
                      GestureDetector(
                        onTap: () => _previewImage(_selectedImages[i]),
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(8),
                            image: DecorationImage(
                              image: FileImage(_selectedImages[i]),
                              fit: BoxFit.cover,
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        top: 4,
                        right: 4,
                        child: GestureDetector(
                          onTap: () => _removeImage(i),
                          child: Container(
                            decoration: BoxDecoration(
                              color: Colors.black54,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(Icons.close, color: Colors.white, size: 20),
                          ),
                        ),
                      ),
                      if (_isUploading)
                        Positioned(
                          bottom: 0,
                          left: 0,
                          right: 0,
                          child: LinearProgressIndicator(
                            value: _uploadProgress[i],
                            backgroundColor: Colors.black12,
                            color: Colors.blueAccent,
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 10),
            if (_selectedImages.isNotEmpty)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isUploading ? null : _uploadImagesToServer,
                  icon: _isUploading
                      ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                  )
                      : Icon(Icons.cloud_done_outlined),
                  label: Text(_isUploading ? "Uploading..." : "Upload"),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 14),
                    textStyle: TextStyle(fontSize: 16),
                  ),
                ),
              ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
