import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Image } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Ionicons } from '@expo/vector-icons';
import api, { getApiUrl } from '../api/api';

export default function Img2PdfScreen() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const pickFiles = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['image/jpeg', 'image/png', 'image/jpg'],
        multiple: true,
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        const picked = result.assets ? result.assets : [result];
        setFiles((prev) => [...prev, ...picked]);
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to pick images');
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const convertFiles = async () => {
    if (files.length === 0) {
      Alert.alert('Error', 'Please select at least 1 image.');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files[]', {
          uri: file.uri,
          name: file.name,
          type: file.mimeType || 'image/jpeg',
        });
      });
      formData.append('separate', 'false'); // Always merge into one for mobile for now

      const response = await api.post('/api/img2pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        const downloadUrl = getApiUrl() + response.data.url;
        const fileUri = FileSystem.documentDirectory + response.data.filename;
        const downloadRes = await FileSystem.downloadAsync(downloadUrl, fileUri);
        
        setLoading(false);
        if (await Sharing.isAvailableAsync()) {
            await Sharing.shareAsync(downloadRes.uri);
        } else {
            Alert.alert('Success', `File saved to: ${downloadRes.uri}`);
        }
        setFiles([]);
      } else {
        throw new Error(response.data.error || 'Conversion failed');
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Something went wrong.');
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
            <Text style={styles.description}>Convert images to a single PDF document.</Text>
        </View>

        <TouchableOpacity style={styles.addButton} onPress={pickFiles}>
          <Ionicons name="images-outline" size={24} color="white" />
          <Text style={styles.addButtonText}>Add Images</Text>
        </TouchableOpacity>

        <View style={styles.grid}>
          {files.map((file, index) => (
            <View key={index} style={styles.imageItem}>
              <Image source={{ uri: file.uri }} style={styles.previewImage} />
              <TouchableOpacity style={styles.removeBtn} onPress={() => removeFile(index)}>
                <Ionicons name="close-circle" size={24} color="#EF4444" />
              </TouchableOpacity>
            </View>
          ))}
        </View>
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity 
            style={[styles.actionButton, files.length === 0 && styles.disabledButton]} 
            onPress={convertFiles}
            disabled={files.length === 0 || loading}
        >
          {loading ? <ActivityIndicator color="white" /> : <Text style={styles.actionBtnText}>Convert to PDF</Text>}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  scroll: { padding: 20 },
  header: { marginBottom: 20 },
  description: { fontSize: 16, color: '#64748B', textAlign: 'center' },
  addButton: {
    backgroundColor: '#10B981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  addButtonText: { color: 'white', fontWeight: '600', fontSize: 16, marginLeft: 8 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  imageItem: { width: '30%', aspectRatio: 1, borderRadius: 8, overflow: 'hidden', position: 'relative' },
  previewImage: { width: '100%', height: '100%' },
  removeBtn: { position: 'absolute', top: 2, right: 2, backgroundColor: 'white', borderRadius: 12 },
  footer: { padding: 20, borderTopWidth: 1, borderTopColor: '#E2E8F0', backgroundColor: 'white' },
  actionButton: { backgroundColor: '#10B981', padding: 16, borderRadius: 12, alignItems: 'center' },
  disabledButton: { backgroundColor: '#94A3B8' },
  actionBtnText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});
