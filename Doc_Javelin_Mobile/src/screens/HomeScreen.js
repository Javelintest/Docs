import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, SafeAreaView, StatusBar, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const tools = [
  { id: 'merge', title: 'Merge PDFs', icon: 'documents-outline', color: '#4F46E5', route: 'Merge' },
  { id: 'img2pdf', title: 'Image to PDF', icon: 'images-outline', color: '#10B981', route: 'Img2Pdf' },
  { id: 'pdf2word', title: 'PDF to Word', icon: 'document-text-outline', color: '#F59E0B', route: 'Pdf2Word' },
  { id: 'pdf2excel', title: 'PDF to Excel', icon: 'grid-outline', color: '#14B8A6', route: 'Pdf2Excel' },
  { id: 'compress', title: 'Compress PDF', icon: 'contract-outline', color: '#2563EB', route: 'Compress' },
  { id: 'edit', title: 'Edit PDF', icon: 'create-outline', color: '#EF4444', route: 'EditPdf' },
];

export default function HomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Doc Javelin</Text>
          <Text style={styles.subtitle}>All your PDF tools in one place.</Text>
        </View>

        <View style={styles.grid}>
          {tools.map((tool) => (
            <TouchableOpacity 
              key={tool.id} 
              style={[styles.card, { borderLeftColor: tool.color, borderLeftWidth: 4 }]}
              onPress={() => navigation.navigate(tool.route)}
            >
              <View style={[styles.iconContainer, { backgroundColor: tool.color + '20' }]}>
                <Ionicons name={tool.icon} size={28} color={tool.color} />
              </View>
              <View style={styles.cardContent}>
                  <Text style={styles.cardTitle}>{tool.title}</Text>
                  <Text style={styles.cardAction}>Open Tool</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#CBD5E1" />
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    marginBottom: 30,
    marginTop: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
    color: '#0F172A',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748B',
  },
  grid: {
    gap: 16,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#64748B',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 3,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E293B',
    marginBottom: 4,
  },
  cardAction: {
    fontSize: 14,
    color: '#94A3B8',
  },
});
