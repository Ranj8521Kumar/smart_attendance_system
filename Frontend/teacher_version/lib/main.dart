import 'package:flutter/material.dart';
import 'login.dart';
import 'forgot_password.dart';
import 'home.dart';
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const TeacherApp());
}

class TeacherApp extends StatelessWidget {
  const TeacherApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Attendance - Teacher',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
        scaffoldBackgroundColor: Colors.white,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/forgot-password': (context) => ForgotPasswordScreen(),
        '/dashboard': (context) => const HomeScreen(),
      },
    );
  }
}
