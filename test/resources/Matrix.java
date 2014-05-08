package battlechap;

import java.io.PrintStream;

public class Matrix {
    private Object[][] _datmatrix;

    public Matrix(int paramInt){
	this._datmatrix = new Object[paramInt][paramInt];
    }

    public int size() {
	return this._datmatrix.length;
    }

    public Object get(int paramInt1, int paramInt2) {
	return this._datmatrix[paramInt1][paramInt2];
    }

    public boolean isEmpty(int paramInt1, int paramInt2) {
	return this._datmatrix[paramInt1][paramInt2] == null;
    }

    public boolean equals(Object paramObject) {
	boolean bool = true;
	if ((paramObject instanceof Matrix)) {
	    Matrix localMatrix = (Matrix)paramObject;
	    if (localMatrix.size() == size()) {
		for (int i = 0; i < size(); i++) {
		    for (int j = 0; j < size(); j++) {
			if (!localMatrix.get(i, j).equals(get(i, j))) {
			    bool = false;
			    break;
			}
		    }
		    if (!bool)
			break;
		}
	    }
	    else
		bool = false;
	}
	else
	    {
		bool = false;
	    }
	return bool;
    }

    public Object set(int paramInt1, int paramInt2, Object paramObject) {
	Object localObject = this._datmatrix[paramInt1][paramInt2];
	this._datmatrix[paramInt1][paramInt2] = paramObject;
	return localObject;
    }

    public void transpose() {
	int i = 0;
	for (int j = 0; j < size(); j++) {
	    for (int k = i; k < size(); k++) {
		set(j, k, set(k, j, get(j, k)));
	    }
	    i++;
	}
    }

    public static void swapRows(int paramInt1, int paramInt2, Object[][] paramArrayOfObject) {
	for (int i = 0; i < paramArrayOfObject[paramInt1].length; i++) {
	    Object localObject = paramArrayOfObject[paramInt1][i];
	    paramArrayOfObject[paramInt1][i] = paramArrayOfObject[paramInt2][i];
	    paramArrayOfObject[paramInt2][i] = localObject;
	}
    }

    public static void swapCols(int paramInt1, int paramInt2, Object[][] paramArrayOfObject) {
	for (int i = 0; i < paramArrayOfObject.length; i++) {
	    Object localObject = paramArrayOfObject[i][paramInt1];
	    paramArrayOfObject[i][paramInt1] = paramArrayOfObject[i][paramInt2];
	    paramArrayOfObject[i][paramInt2] = localObject;
	}
    }

    public Object[] getRow(int paramInt) {
	Object[] arrayOfObject = new Object[this._datmatrix[paramInt].length];
	for (int i = 0; i < arrayOfObject.length; i++) {
	    arrayOfObject[i] = this._datmatrix[paramInt][i];
	}
	return arrayOfObject;
    }

    public Object[] getCol(int paramInt) {
	Object[] arrayOfObject = new Object[this._datmatrix[paramInt].length];
	for (int i = 0; i < arrayOfObject.length; i++) {
	    arrayOfObject[i] = this._datmatrix[i][paramInt];
	}
	return arrayOfObject;
    }

    public Object[] setRow(int paramInt, Object[] paramArrayOfObject) {
	Object[] arrayOfObject = getRow(paramInt);

	for (int i = 0; i < size(); i++) {
	    set(paramInt, i, paramArrayOfObject[i]);
	}

	return arrayOfObject;
    }

    public Object[] setCol(int paramInt, Object[] paramArrayOfObject) {
	Object[] arrayOfObject = getCol(paramInt);

	for (int i = 0; i < size(); i++) {
	    set(i, paramInt, paramArrayOfObject[i]);
	}

	return arrayOfObject;
    }

    public String toString()
    {
	String str1 = "";
	for (int i = 0; i < this._datmatrix.length; i++) {
	    if (i < 9)
		str1 = str1 + (i + 1) + ": ";
	    else
		str1 = str1 + (i + 1) + ":";
	    for (int j = 0; j < this._datmatrix[i].length; j++) {
		int k = (this._datmatrix[i][j] + "").length();
		String str2 = "   ".substring(k);
		str1 = str1 + this._datmatrix[i][j] + str2;
	    }
	    str1 = str1 + "\n";
	}
	return str1;
    }

    public static void print(Object[][] paramArrayOfObject) {
	for (int i = 0; i < paramArrayOfObject.length; i++) {
	    for (int j = 0; j < paramArrayOfObject[i].length; j++) {
		int k = (paramArrayOfObject[i][j] + "").length();
		String str = "     ".substring(k);
		System.out.print(paramArrayOfObject[i][j] + str);
	    }
	    System.out.print("\n");
	}
    }

    public static void printArray(Object[] paramArrayOfObject) {
	for (int i = 0; i < paramArrayOfObject.length; i++) {
	    int j = (paramArrayOfObject[i] + "").length();
	    String str = "     ".substring(j);
	    System.out.print(paramArrayOfObject[i] + str);
	}
	System.out.print("\n");
    }

    public static void main(String[] paramArrayOfString) {
	Matrix localMatrix1 = new Matrix(5);
	Matrix localMatrix2 = new Matrix(5);
	for (int i = 0; i < localMatrix1.size(); i++) {
	    for (int j = 0; j < localMatrix1.size(); j++) {
		Integer localInteger1 = new Integer((int)(Math.random() * 20.0D));
		localMatrix1.set(i, j, localInteger1);
		localMatrix2.set(i, j, localInteger1);
	    }
	}

	System.out.println("\nDemonstrating equals method (should be true)\t" + localMatrix2.equals(localMatrix1) + "\n");

	System.out.println("Demonstrating get method\n" + localMatrix1.get(0, 0) + "\n");
	System.out.println("Demonstrating is empty method\n" + localMatrix1.isEmpty(1, 0) + "\n");
	System.out.println("Demonstrating size method \n" + localMatrix1.size() + "\n");
	System.out.println("Demonstrating toString method\n" + localMatrix1 + "\n");
	localMatrix1.transpose();
	System.out.println("Blop has been transposed\n" + localMatrix1 + "\n");

	Object[][] arrayOfObject = new Object[4][4];
	for (int j = 0; j < arrayOfObject.length; j++) {
	    for (int k = 0; k < arrayOfObject[j].length; k++) {
		Integer localInteger2 = new Integer((int)(Math.random() * 20.0D));
		arrayOfObject[j][k] = localInteger2;
	    }
	}
	System.out.println("\n\n**Swapping Rows Demo**");
	print(arrayOfObject);
	System.out.println("\nRows 1 and 2 have been Swapped \n");
	swapRows(1, 2, arrayOfObject);
	print(arrayOfObject);

	System.out.println("\n**Swapping Columns Demo**");
	print(arrayOfObject);
	System.out.println("\n\nColumns 1 and 2 have been Swapped \n");
	swapCols(1, 2, arrayOfObject);
	print(arrayOfObject);

	System.out.println("\n**Getting rows demo (from blop)**");
	System.out.println(localMatrix1);
	System.out.println("\nGetting row 1\n");
	printArray(localMatrix1.getRow(1));

	System.out.println("\n**Getting cols demo (from blop)**");
	System.out.println(localMatrix1);
	System.out.println("\nGetting col 1\n");
	printArray(localMatrix1.getCol(1));

	System.out.println("\n**Demonstrating set row method**");
	System.out.println(localMatrix1);
	System.out.println("\nSwitching row 1 of blop to 1st column of blop\n");
	localMatrix1.setRow(1, localMatrix1.getCol(1));
	System.out.println(localMatrix1 + "\n");

	System.out.println("\n**Demonstrating set col method**");
	System.out.println(localMatrix1);
	System.out.println("\nSwitching col 1 of blop to 2nd row of blop\n");
	localMatrix1.setCol(1, localMatrix1.getRow(2));
	System.out.println(localMatrix1 + "\n");
    }
}

