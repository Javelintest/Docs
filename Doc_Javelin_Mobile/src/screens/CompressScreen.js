import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Ionicons } from '@expo/vector-icons';
import api, { getApiUrl } from '../api/api';

export default function CompressScreen() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        multiple: false,
        copyToCacheDirectory: true,
      });

      if (!result.canceled) {
        setFile(result.assets ? result.assets[0] : result);
      }
    } catch (err) {
      Alert.alert('Error', 'Failed to pick file');
    }
  };

  const compressFile = async () => {
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        name: file.name,
        type: 'application/pdf',
      });

      const response = await api.post('/api/compress', formData, {
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
        setFile(null);
      } else {
        throw new Error(response.data.error || 'Compression failed');
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
            <Text style={styles.description}>Reduce file size of your PDF documents.</Text>
        </View>

        {!file ? (
          <TouchableOpacity style={styles.uploadArea} onPress={pickFile}>
            <Ionicons name="contract-outline" size={48} color="#2563EB" />
            <Text style={styles.uploadText}>Tap to Select PDF</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.fileCard}>
             <Ionicons name="document-text" size={32} color="#2563EB" />
             <Text style={styles.fileName}>{file.name}</Text>
             <TouchableOpacity onPress={() => setFile(null)}>
                <Ionicons name="close-circle" size={24} color="#EF4444" />
             </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <TouchableOpacity 
            style={[styles.actionButton, !file && styles.disabledButton]} 
            onPress={compressFile}
            disabled={!file || loading}
        >
          {loading ? <ActivityIndicator color="white" /> : <Text style={styles.actionBtnText}>Compress PDF</Text>}
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
  uploadArea: {
    borderWidth: 2, borderColor: '#2563EB', borderStyle: 'dashed',
    borderRadius: 16, height: 200, alignItems: 'center', justifyContent: 'center', backgroundColor: '#EFF6FF'
  },
  uploadText: { marginTop: 12, color: '#1D4ED8', fontWeight: '600' },
  fileCard: { 
    flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', padding: 16, 
    borderRadius: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 
   },
  fileName: { flex: 1, marginHorizontal: 12, fontSize: 16 },
  footer: { padding: 20, borderTopWidth: 1, borderTopColor: '#E2E8F0', backgroundColor: 'white' },
  actionButton: { backgroundColor: '#2563EB', padding: 16, borderRadius: 12, alignItems: 'center' },
  disabledButton: { backgroundColor: '#93C5FD' },
  actionBtnText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});
