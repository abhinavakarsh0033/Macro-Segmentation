import os
from torch.utils.data import Dataset
from datasets import load_dataset

class CustomDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.dataset = load_dataset("FanqingM/MMIU-Benchmark", split="test")
        self.idx = 0

        # For now flattening as a list of images... Will decide later if want to keep them grouped
        self.__image_paths = []
        for item in self.dataset:
            for path in item["input_image_path"]:
                # Remove leading "./" if present
                clean_path = path.lstrip("./")
                abs_path = os.path.join(self.image_dir, clean_path)
                self.__image_paths.append(abs_path)
        print(f"Dataset initialized with {len(self.__image_paths)} images.")

    def __len__(self):
        return len(self.__image_paths)

    def __getitem__(self, idx):
        return self.__image_paths[idx]
    
    def get_next_image(self):
        if self.idx >= len(self.__image_paths):
            raise IndexError("No more images in the dataset.")
        image_path = self.__image_paths[self.idx]
        self.idx += 1
        return image_path
    
    def get_images(self, count):
        if self.idx + count > len(self.__image_paths):
            raise IndexError("Not enough images left in the dataset.")
        image_paths = self.__image_paths[self.idx:self.idx + count]
        self.idx += count
        return image_paths