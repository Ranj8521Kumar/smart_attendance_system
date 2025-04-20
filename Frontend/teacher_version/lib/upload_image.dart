import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;

class SubjectUploadPage extends StatefulWidget {
  final String subject;

  const SubjectUploadPage({Key? key, required this.subject}) : super(key: key);

  @override
  _SubjectUploadPageState createState() => _SubjectUploadPageState();
}

class _SubjectUploadPageState extends State<SubjectUploadPage> {
  List<File> _selectedImages = [];

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
        _selectedImages.addAll(result.files.map((f) => File(f.path!)));
      });
    }
  }

  Future<void> _uploadImagesToServer() async {
    final uri = Uri.parse('http://192.168.25.109:5000/upload_images'); // Update with your server IP
    final request = http.MultipartRequest('POST', uri);
    request.fields['subject'] = widget.subject;

    try {
      for (var image in _selectedImages) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'images', // Key used in backend
            image.path,
          ),
        );
      }

      final response = await request.send();

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Images uploaded successfully!')),
        );
        setState(() {
          _selectedImages.clear();
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed. Try again.')),
        );
      }
    } catch (e) {
      print('Upload error: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Something went wrong.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final subjectText = "Subject: ${widget.subject}";

    return Scaffold(
      appBar: AppBar(title: Text("Upload Images")),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Column(
          children: [
            const SizedBox(height: 20),

            // Subject text
            Text(
              subjectText,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 200),

            // Upload icon and prompt
            Center(
              child: GestureDetector(
                onTap: _showPickerOptions,
                child: Column(
                  children: [
                    Icon(
                      Icons.cloud_upload_outlined,
                      size: 100,
                      color: Colors.blueAccent,
                    ),
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

            // Image previews
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
                  itemBuilder: (ctx, i) => Image.file(
                    _selectedImages[i],
                    fit: BoxFit.cover,
                  ),
                ),
              ),

            const SizedBox(height: 10),

            // Upload button
            if (_selectedImages.isNotEmpty)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _uploadImagesToServer,
                  icon: Icon(Icons.cloud_done_outlined),
                  label: Text("Upload"),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 14),
                    textStyle: TextStyle(fontSize: 16),
                  ),
                ),
              ),
           const SizedBox(height: 20,)
          ],
        ),
      ),
    );
  }
}
