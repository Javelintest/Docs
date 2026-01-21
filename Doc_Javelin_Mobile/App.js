import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';

import HomeScreen from './src/screens/HomeScreen';
import MergeScreen from './src/screens/MergeScreen';
import Img2PdfScreen from './src/screens/Img2PdfScreen';
import Pdf2WordScreen from './src/screens/Pdf2WordScreen';
import Pdf2ExcelScreen from './src/screens/Pdf2ExcelScreen';
import CompressScreen from './src/screens/CompressScreen';
import EditPdfScreen from './src/screens/EditPdfScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator 
        initialRouteName="Home"
        screenOptions={{
            headerStyle: { backgroundColor: 'white', shadowColor: 'transparent' },
            headerTitleStyle: { fontWeight: '600', color: '#0F172A' },
            headerTintColor: '#0F172A',
        }}
      >
        <Stack.Screen 
            name="Home" 
            component={HomeScreen} 
            options={{ headerShown: false }}
        />
        <Stack.Screen name="Merge" component={MergeScreen} options={{ title: 'Merge PDFs' }} />
        <Stack.Screen name="Img2Pdf" component={Img2PdfScreen} options={{ title: 'Images to PDF' }} />
        <Stack.Screen name="Pdf2Word" component={Pdf2WordScreen} options={{ title: 'PDF to Word' }} />
        <Stack.Screen name="Pdf2Excel" component={Pdf2ExcelScreen} options={{ title: 'PDF to Excel' }} />
        <Stack.Screen name="Compress" component={CompressScreen} options={{ title: 'Compress PDF' }} />
        <Stack.Screen name="EditPdf" component={EditPdfScreen} options={{ title: 'Edit PDF' }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
