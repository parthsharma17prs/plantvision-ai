import os
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class PlantDocPreprocessor:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.train_path = os.path.join(dataset_path, 'train')
        self.test_path = os.path.join(dataset_path, 'test')
        self.classes = []
        self.dataset_info = {}
        self.corrupted_images = []
        self.invalid_images = []
        
    def analyze_dataset_structure(self):
        """Analyze the dataset structure and count images per class"""
        print("=== Dataset Structure Analysis ===")
        
        # Get all classes
        self.classes = [d for d in os.listdir(self.train_path) 
                       if os.path.isdir(os.path.join(self.train_path, d))]
        self.classes.sort()
        
        print(f"Total classes: {len(self.classes)}")
        print(f"Classes: {self.classes}")
        
        # Count images in train and test
        train_counts = {}
        test_counts = {}
        
        for class_name in self.classes:
            train_class_path = os.path.join(self.train_path, class_name)
            test_class_path = os.path.join(self.test_path, class_name)
            
            train_images = [f for f in os.listdir(train_class_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            test_images = [f for f in os.listdir(test_class_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
            
            train_counts[class_name] = len(train_images)
            test_counts[class_name] = len(test_images)
        
        self.dataset_info = {
            'classes': self.classes,
            'train_counts': train_counts,
            'test_counts': test_counts,
            'total_train_images': sum(train_counts.values()),
            'total_test_images': sum(test_counts.values())
        }
        
        print(f"\nTotal train images: {self.dataset_info['total_train_images']}")
        print(f"Total test images: {self.dataset_info['total_test_images']}")
        print(f"Total images: {self.dataset_info['total_train_images'] + self.dataset_info['total_test_images']}")
        
        return self.dataset_info
    
    def check_image_integrity(self):
        """Check for corrupted or invalid images"""
        print("\n=== Image Integrity Check ===")
        
        def check_images_in_directory(directory_path, class_name):
            corrupted = []
            invalid = []
            
            for img_file in os.listdir(directory_path):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    img_path = os.path.join(directory_path, img_file)
                    
                    try:
                        # Check if file can be opened
                        with Image.open(img_path) as img:
                            # Check if image has valid dimensions
                            if img.size[0] <= 0 or img.size[1] <= 0:
                                invalid.append(img_path)
                            
                            # Check if image mode is valid
                            if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                                invalid.append(img_path)
                                
                    except Exception as e:
                        corrupted.append(img_path)
                        print(f"Corrupted image: {img_path} - Error: {str(e)}")
            
            return corrupted, invalid
        
        total_corrupted = 0
        total_invalid = 0
        
        for class_name in self.classes:
            train_class_path = os.path.join(self.train_path, class_name)
            test_class_path = os.path.join(self.test_path, class_name)
            
            train_corrupted, train_invalid = check_images_in_directory(train_class_path, f"{class_name}_train")
            test_corrupted, test_invalid = check_images_in_directory(test_class_path, f"{class_name}_test")
            
            self.corrupted_images.extend(train_corrupted + test_corrupted)
            self.invalid_images.extend(train_invalid + test_invalid)
            
            total_corrupted += len(train_corrupted) + len(test_corrupted)
            total_invalid += len(train_invalid) + len(test_invalid)
        
        print(f"\nCorrupted images found: {total_corrupted}")
        print(f"Invalid images found: {total_invalid}")
        print(f"Total problematic images: {total_corrupted + total_invalid}")
        
        return self.corrupted_images, self.invalid_images
    
    def get_image_statistics(self):
        """Get detailed statistics about image dimensions and sizes"""
        print("\n=== Image Statistics ===")
        
        dimensions = []
        file_sizes = []
        
        for split_path in [self.train_path, self.test_path]:
            for class_name in self.classes:
                class_path = os.path.join(split_path, class_name)
                
                for img_file in os.listdir(class_path):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                        img_path = os.path.join(class_path, img_file)
                        
                        try:
                            # Skip corrupted images
                            if img_path in self.corrupted_images or img_path in self.invalid_images:
                                continue
                                
                            with Image.open(img_path) as img:
                                dimensions.append(img.size)
                                file_sizes.append(os.path.getsize(img_path))
                        except:
                            continue
        
        if dimensions:
            widths, heights = zip(*dimensions)
            
            stats = {
                'min_width': min(widths),
                'max_width': max(widths),
                'avg_width': np.mean(widths),
                'min_height': min(heights),
                'max_height': max(heights),
                'avg_height': np.mean(heights),
                'min_file_size': min(file_sizes),
                'max_file_size': max(file_sizes),
                'avg_file_size': np.mean(file_sizes),
                'total_images_analyzed': len(dimensions)
            }
            
            print(f"Images analyzed: {stats['total_images_analyzed']}")
            print(f"Width range: {stats['min_width']} - {stats['max_width']} (avg: {stats['avg_width']:.1f})")
            print(f"Height range: {stats['min_height']} - {stats['max_height']} (avg: {stats['avg_height']:.1f})")
            print(f"File size range: {stats['min_file_size']/1024:.1f}KB - {stats['max_file_size']/1024:.1f}KB (avg: {stats['avg_file_size']/1024:.1f}KB)")
            
            return stats
        else:
            print("No valid images found for analysis")
            return None
    
    def clean_dataset(self, remove_corrupted=True):
        """Clean the dataset by removing corrupted and invalid images"""
        print("\n=== Dataset Cleaning ===")
        
        problematic_images = self.corrupted_images + self.invalid_images
        
        if not problematic_images:
            print("No problematic images found. Dataset is clean.")
            return True
        
        print(f"Found {len(problematic_images)} problematic images:")
        
        for img_path in problematic_images:
            print(f"  - {img_path}")
        
        if remove_corrupted:
            removed_count = 0
            for img_path in problematic_images:
                try:
                    os.remove(img_path)
                    removed_count += 1
                    print(f"Removed: {img_path}")
                except Exception as e:
                    print(f"Failed to remove {img_path}: {str(e)}")
            
            print(f"\nSuccessfully removed {removed_count} problematic images")
            return True
        else:
            print("Problematic images not removed (remove_corrupted=False)")
            return False
    
    def create_dataset_dataframe(self):
        """Create a pandas DataFrame with dataset information"""
        print("\n=== Creating Dataset DataFrame ===")
        
        data = []
        
        for split in ['train', 'test']:
            split_path = self.train_path if split == 'train' else self.test_path
            
            for class_name in self.classes:
                class_path = os.path.join(split_path, class_name)
                
                for img_file in os.listdir(class_path):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                        img_path = os.path.join(class_path, img_file)
                        
                        # Skip corrupted images
                        if img_path in self.corrupted_images or img_path in self.invalid_images:
                            continue
                        
                        try:
                            with Image.open(img_path) as img:
                                data.append({
                                    'filename': img_file,
                                    'filepath': img_path,
                                    'class': class_name,
                                    'split': split,
                                    'width': img.size[0],
                                    'height': img.size[1],
                                    'mode': img.mode,
                                    'file_size': os.path.getsize(img_path)
                                })
                        except:
                            continue
        
        df = pd.DataFrame(data)
        print(f"DataFrame created with {len(df)} valid images")
        
        return df
    
    def generate_report(self, save_path='plantdoc_preprocessing_report.txt'):
        """Generate a comprehensive preprocessing report"""
        print("\n=== Generating Preprocessing Report ===")
        
        report = []
        report.append("=" * 60)
        report.append("PLANTDOC DATASET PREPROCESSING REPORT")
        report.append("=" * 60)
        report.append(f"Dataset Path: {self.dataset_path}")
        report.append(f"Analysis Date: {pd.Timestamp.now()}")
        report.append("")
        
        # Dataset structure
        report.append("DATASET STRUCTURE:")
        report.append(f"Total Classes: {len(self.classes)}")
        report.append(f"Total Train Images: {self.dataset_info['total_train_images']}")
        report.append(f"Total Test Images: {self.dataset_info['total_test_images']}")
        report.append(f"Total Images: {self.dataset_info['total_train_images'] + self.dataset_info['total_test_images']}")
        report.append("")
        
        # Class distribution
        report.append("CLASS DISTRIBUTION:")
        report.append("Class Name\t\tTrain\tTest\tTotal")
        report.append("-" * 50)
        
        for class_name in self.classes:
            train_count = self.dataset_info['train_counts'][class_name]
            test_count = self.dataset_info['test_counts'][class_name]
            total = train_count + test_count
            report.append(f"{class_name:<25}\t{train_count}\t{test_count}\t{total}")
        
        report.append("")
        
        # Image integrity
        report.append("IMAGE INTEGRITY:")
        report.append(f"Corrupted Images: {len(self.corrupted_images)}")
        report.append(f"Invalid Images: {len(self.invalid_images)}")
        report.append(f"Total Problematic: {len(self.corrupted_images) + len(self.invalid_images)}")
        
        if self.corrupted_images:
            report.append("\nCorrupted Images:")
            for img in self.corrupted_images:
                report.append(f"  - {img}")
        
        if self.invalid_images:
            report.append("\nInvalid Images:")
            for img in self.invalid_images:
                report.append(f"  - {img}")
        
        report.append("")
        
        # Statistics
        stats = self.get_image_statistics()
        if stats:
            report.append("IMAGE STATISTICS:")
            report.append(f"Images Analyzed: {stats['total_images_analyzed']}")
            report.append(f"Width Range: {stats['min_width']} - {stats['max_width']} (avg: {stats['avg_width']:.1f})")
            report.append(f"Height Range: {stats['min_height']} - {stats['max_height']} (avg: {stats['avg_height']:.1f})")
            report.append(f"File Size Range: {stats['min_file_size']/1024:.1f}KB - {stats['max_file_size']/1024:.1f}KB")
            report.append(f"Average File Size: {stats['avg_file_size']/1024:.1f}KB")
        
        report.append("")
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)
        
        # Save report
        report_text = '\n'.join(report)
        with open(save_path, 'w') as f:
            f.write(report_text)
        
        print(f"Report saved to: {save_path}")
        print("\nReport Preview:")
        print(report_text[:1000] + "..." if len(report_text) > 1000 else report_text)
        
        return report_text
    
    def visualize_dataset(self, save_plots=True):
        """Create visualizations of the dataset"""
        print("\n=== Creating Dataset Visualizations ===")
        
        # Class distribution plot
        plt.figure(figsize=(15, 8))
        
        classes = list(self.dataset_info['train_counts'].keys())
        train_counts = list(self.dataset_info['train_counts'].values())
        test_counts = list(self.dataset_info['test_counts'].values())
        
        x = np.arange(len(classes))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(15, 8))
        rects1 = ax.bar(x - width/2, train_counts, width, label='Train', alpha=0.8)
        rects2 = ax.bar(x + width/2, test_counts, width, label='Test', alpha=0.8)
        
        ax.set_xlabel('Classes')
        ax.set_ylabel('Number of Images')
        ax.set_title('PlantDoc Dataset: Class Distribution')
        ax.set_xticks(x)
        ax.set_xticklabels(classes, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('plantdoc_class_distribution.png', dpi=300, bbox_inches='tight')
            print("Class distribution plot saved as: plantdoc_class_distribution.png")
        
        plt.show()
        
        # Create pie charts for train and test distributions
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Train distribution
        ax1.pie(train_counts, labels=classes, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Train Set Distribution')
        
        # Test distribution
        ax2.pie(test_counts, labels=classes, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Test Set Distribution')
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('plantdoc_pie_charts.png', dpi=300, bbox_inches='tight')
            print("Pie charts saved as: plantdoc_pie_charts.png")
        
        plt.show()

def main():
    # Initialize preprocessor
    dataset_path = "c:/Users/HARSH/Desktop/archive (4)/PlantDoc-Dataset"
    preprocessor = PlantDocPreprocessor(dataset_path)
    
    # Step 1: Analyze dataset structure
    dataset_info = preprocessor.analyze_dataset_structure()
    
    # Step 2: Check image integrity
    corrupted, invalid = preprocessor.check_image_integrity()
    
    # Step 3: Get image statistics
    stats = preprocessor.get_image_statistics()
    
    # Step 4: Clean dataset (optional - set to False if you want to keep corrupted files)
    clean_success = preprocessor.clean_dataset(remove_corrupted=False)
    
    # Step 5: Create DataFrame
    df = preprocessor.create_dataset_dataframe()
    
    # Step 6: Generate report
    report = preprocessor.generate_report()
    
    # Step 7: Create visualizations
    preprocessor.visualize_dataset()
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"Total classes processed: {len(preprocessor.classes)}")
    print(f"Total valid images: {len(df)}")
    print(f"Problematic images found: {len(corrupted) + len(invalid)}")
    print("Report saved as: plantdoc_preprocessing_report.txt")
    print("Visualizations saved as PNG files")
    
    return preprocessor, df, stats

if __name__ == "__main__":
    preprocessor, df, stats = main()
