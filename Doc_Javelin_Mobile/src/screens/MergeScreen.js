import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Ionicons } from '@expo/vector-icons';
import api, { getApiUrl } from '../api/api';

export default function MergeScreen() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);

  const pickFiles = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        multiple: true,
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        // Expo Document Picker returns assets array in new versions, or single object in old
        const picked = result.assets ? result.assets : [result];
        setFiles((prev) => [...prev, ...picked]);
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to pick files');
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const mergeFiles = async () => {
    if (files.length < 2) {
      Alert.alert('Error', 'Please select at least 2 PDF files to merge.');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files[]', {
          uri: file.uri,
          name: file.name,
          type: 'application/pdf',
        });
      });

      // 1. Upload and Merge
      const response = await api.post('/api/merge', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        // 2. Download the Result
        const downloadUrl = getApiUrl() + response.data.url;
        const fileUri = FileSystem.documentDirectory + response.data.filename;

        const downloadRes = await FileSystem.downloadAsync(downloadUrl, fileUri);
        
        setLoading(false);
        
        // 3. Share / Save
        if (await Sharing.isAvailableAsync()) {
            await Sharing.shareAsync(downloadRes.uri);
        } else {
            Alert.alert('Success', `File downloaded to: ${downloadRes.uri}`);
        }
        
        // Reset
        setFiles([]);
      } else {
        throw new Error(response.data.error || 'Merge failed');
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Something went wrong. Ensure backend is running.');
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
            <Text style={styles.description}>Select multiple PDF files to combine them into one.</Text>
        </View>

        <TouchableOpacity style={styles.addButton} onPress={pickFiles}>
          <Ionicons name="add-circle-outline" size={24} color="white" />
          <Text style={styles.addButtonText}>Add PDF Files</Text>
        </TouchableOpacity>

        {files.length > 0 && (
          <View style={styles.fileList}>
            {files.map((file, index) => (
              <View key={index} style={styles.fileItem}>
                <Ionicons name="document-text" size={24} color="#4F46E5" />
                <Text style={styles.fileName} numberOfLines={1}>{file.name}</Text>
                <TouchableOpacity onPress={() => removeFile(index)}>
                  <Ionicons name="close-circle" size={24} color="#EF4444" />
                </TouchableOpacity>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity 
            style={[styles.mergeButton, files.length < 2 && styles.disabledButton]} 
            onPress={mergeFiles}
            disabled={files.length < 2 || loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.mergeButtonText}>Merge {files.length} Files</Text>
          )}
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
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  addButtonText: { color: 'white', fontWeight: '600', fontSize: 16, marginLeft: 8 },
  fileList: { gap: 12 },
  fileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  fileName: { flex: 1, marginHorizontal: 12, fontSize: 14, color: '#334155' },
  footer: { padding: 20, borderTopWidth: 1, borderTopColor: '#E2E8F0', backgroundColor: 'white' },
  mergeButton: {
    backgroundColor: '#4F46E5',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  disabledButton: { backgroundColor: '#94A3B8' },
  mergeButtonText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});
