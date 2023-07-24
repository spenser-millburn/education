
# Chapter 4 -  Karnaugh Maps
-----

## Three Variable K-Maps

-----

### 1. Use a k-map to find a minimum SOP expression for : $F(A, B, C) = Σm(0, 1, 3, 4, 6)$




### Truth Table



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>A</th>
      <th>B</th>
      <th>C</th>
      <th>F</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



### KMAP



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



    



### KMAP Legend



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>6</td>
      <td>7</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>4</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



    


### Minimum SOP form
To find the minimum SOP expression, first group all adjacent 1s:

GROUPS: $[0,1],[1,3],[6,4] = A'B' + A'C + AC'$

𝐴′𝐵′+𝐴′𝐶+𝐴𝐶′                                                                                                                                                                       
= 𝐴′(𝐵′+𝐶) + 𝐴𝐶′   (Distributive law)                                                                                                                                              
-----

### 3. Identify all of the implicants contained in $F(A, B, C) = A ⊕ B + B′C′.$




### Truth Table



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>A</th>
      <th>B</th>
      <th>C</th>
      <th>F</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### KMAP



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



    



### KMAP Legend



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>6</td>
      <td>7</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>4</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



    


IMPLICANTS = $\textbf{groups_of_one}([0],[2],[3],[4],[5]),\textbf{groups_of_two}([0,2],[2,3],[0,4],[4,5])$

PRIME IMPLICANTS = $[0,2],[2,3],[0,4],[4,5] = A'C' + A'B + B'C +AB'$

ESSENTIAL PRIME IMPLICANTS= $[0,2],[2,3],[4,5] = A'C' + A'B +AB'$


------

### 5. $F(A, B, C) = A′C + AB′$ and $G(A, B, C) = (A′ + C′)(B′ + C)(A + C)$ are equivalent expressions. Use a k-map to determine which term(s) must be don’t cares.



    F(A, B, C) = A′C + AB



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>1</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>


    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>6</td>
      <td>7</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>4</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>





    





    (𝐴′+𝐶′)(𝐵′+𝐶)(𝐴+𝐶)



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'</th>
      <th>C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>6</td>
      <td>7</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>4</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>





    



Therefore, since minterm 5 is the only one that is not shared, it must be a don't care. 

----

## Four Variable K-Maps

----

### 1. Use a k-map to find a minimum SOP expression for $F (A, B, C, D) = ΠM (0, 3, 4, 8, 9, 10, 14)$




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>4</td>
      <td>5</td>
      <td>7</td>
      <td>6</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>12</td>
      <td>13</td>
      <td>15</td>
      <td>14</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>8</td>
      <td>9</td>
      <td>11</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



    


group ones to find F

#### Prime Implicants $ = [0,4],[8,0],[11,3]$

Minimum SOP:

$ F = A'C'D' + B'C'D' + B'CD$

-----

### 3. Use a k-map to find a minimum POS expression for $F (A, B, C, D) = Σm(1, 3, 4, 5, 6, 12, 14, 15)$




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>1</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>4</td>
      <td>5</td>
      <td>7</td>
      <td>6</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>12</td>
      <td>13</td>
      <td>15</td>
      <td>14</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>8</td>
      <td>9</td>
      <td>11</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



    


group zeros to find F'

#### Prime Implicants $= [8,9,11,10],[9,13],[7],[0,2,8,10]$

$ F' = AB' + AC'D + A'BCD + B'D'$

Solve for F to find POS using demorgans law 

$F'' = (AB' + AC'D + A'BCD + B'D')$

$F'' = (A' + B)(A + C' + D')(A + B'+ C' +D')(B + D)$


-----


### 4. A sensor is capable of determining whether or not a car is speeding (driving faster than the speed limit) or driving dangerously (driving 10 m.p.h. or more above the speed limit). 

### The sensor receives the codes given in table 4.6, where AB corresponds to the speed limit and CD corresponds to the speed of the vehicle. Use a k-map to solve for F (as either minimum SOP or minimum POS), which indicates if the car is speeding.

$ $

|AB |Speed Limit |CD |Car’s Speed
|----|---------|-|-------------|
|00 | 45 m.p.h.|00| < 45 m.p.h.|
|01 |55 m.p.h. |01| 46–55 m.p.h.|
|10 |65 m.p.h. |10| 56–65 m.p.h.|
|11 | unused   |11| 66–75 m.p.h.|




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>x</td>
      <td>x</td>
      <td>x</td>
      <td>x</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



    



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead tr th {
        text-align: left;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>00</th>
      <th>01</th>
      <th>11</th>
      <th>10</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C'D'</th>
      <th>C'D</th>
      <th>CD</th>
      <th>CD'</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>00</th>
      <th>A'B'</th>
      <td>0</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
    </tr>
    <tr>
      <th>01</th>
      <th>A'B</th>
      <td>4</td>
      <td>5</td>
      <td>7</td>
      <td>6</td>
    </tr>
    <tr>
      <th>11</th>
      <th>AB</th>
      <td>12</td>
      <td>13</td>
      <td>15</td>
      <td>14</td>
    </tr>
    <tr>
      <th>10</th>
      <th>AB'</th>
      <td>8</td>
      <td>9</td>
      <td>11</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



    


From KMAP: 

$F  = [3,2,7,6],[3,7,11,15],[1,3,2] = A'C + CD + A'B'$

-----

## Prime Implicant Tables

-----

### 1. 


```python

```
